"""Run: python -m school_pipeline.flow [--extract-only] [--replay RUN_DIR]."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import dlt

ROOT = Path(__file__).resolve().parents[1]
(ROOT / ".state/prefect").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("PREFECT_HOME", str(ROOT / ".state/prefect"))
os.environ.setdefault("PREFECT_SERVER_ANALYTICS_ENABLED", "false")
# Allow slow local/WSL cold starts without overriding an explicit user setting.
os.environ.setdefault("PREFECT_SERVER_EPHEMERAL_STARTUP_TIMEOUT_SECONDS", "90")
os.environ.setdefault("PREFECT_API_DATABASE_CONNECTION_URL", f"sqlite+aiosqlite:///{ROOT / '.state/prefect/prefect.db'}")
os.environ.setdefault("DLT_DATA_DIR", str(ROOT / ".state/dlt"))
from prefect import flow, task
from school_pipeline.transform import school, statistics, surveys
API = "https://api.skolverket.se/planned-educations/v4/school-units"
REGISTER = "https://api.skolverket.se/skolenhetsregistret/v2/school-units"


def endpoints(code):
    return {"register": f"{REGISTER}/{code}", "statistics": f"{API}/{code}/statistics/gr",
            "parents": f"{API}/{code}/nestedsurveys/custodiansgr",
            "pupils": f"{API}/{code}/nestedsurveys/pupilsgr"}


@task(retries=2, retry_delay_seconds=5, persist_result=False)
def retrieve(code, kind, url, run_dir):
    headers = {"User-Agent": "SchoolCourseProject/0.1 (public county data)",
               "Accept": "application/json" if kind == "register" else
               "application/vnd.skolverket.plannededucations.api.v4.hal+json"}
    if kind != "register":
        headers["X-API-Version"] = "v4"
    try:
        with urlopen(Request(url, headers=headers), timeout=45) as response:
            raw = response.read(5_000_001)
            if len(raw) > 5_000_000:
                raise ValueError("Response exceeds size limit")
            content_type = response.headers.get("Content-Type", "")
    except HTTPError as exc:
        if exc.code in {404, 204}:
            return {"code": code, "kind": kind, "url": url, "status": "UNAVAILABLE", "http_status": exc.code}
        raise RuntimeError(f"Public API returned HTTP {exc.code}") from None
    except URLError:
        raise RuntimeError("Public API connection failed") from None
    payload = json.loads(raw)
    path = Path(run_dir) / f"{code}_{kind}.json"
    # Register contacts are unnecessary personal data: remove before persisting.
    if kind == "register":
        attrs = payload.get("data", {}).get("attributes", {})
        for field in ("headMaster", "email", "phoneNumber"):
            attrs.pop(field, None)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    time.sleep(0.3)
    return {"code": code, "kind": kind, "url": url, "status": "FETCHED",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "content_type": content_type, "file": path.name}


def prepare(manifest, run_dir):
    tables = {"schools": [], "statistics": [], "survey_observations": [], "source_coverage": []}
    for entry in manifest["sources"]:
        tables["source_coverage"].append({k: v for k, v in entry.items() if k != "file"})
        if entry["status"] != "FETCHED":
            continue
        payload = json.loads((Path(run_dir) / entry["file"]).read_text(encoding="utf-8"))
        provenance = {"source_url": entry["url"], "retrieved_at": entry["retrieved_at"],
                      "response_sha256": entry["response_sha256"]}
        code, kind = entry["code"], entry["kind"]
        if kind == "register":
            rows, table = [school(payload, code, provenance)], "schools"
        elif kind == "statistics":
            rows, table = statistics(payload, code, provenance), "statistics"
        else:
            rows, table = surveys(payload, code, kind, provenance), "survey_observations"
        tables[table].extend(rows)
        tables["source_coverage"][-1]["normalized_rows"] = len(rows)
        tables["source_coverage"][-1]["data_status"] = "ROWS" if rows else "EMPTY_BODY_NO_OBSERVATIONS"
    for name, rows in tables.items():
        with (Path(run_dir) / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {"run_id": manifest["run_id"], "rows": {k: len(v) for k, v in tables.items()},
               "source_status_counts": dict(Counter(e["status"] for e in manifest["sources"])),
               "statistics_value_types": dict(Counter(r["value_type"] for r in tables["statistics"])),
               "survey_value_statuses": dict(Counter(r["value_status"] for r in tables["survey_observations"]))}
    (Path(run_dir) / "coverage.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return tables


@task(persist_result=False)
def load_sqlite(tables, database_path=None, pipelines_dir=None):
    # Snapshot replacement avoids append duplication and stale/suppressed observations.
    # This database/dataset is exclusively for the configured selected sample.
    resources = []
    for name, rows in tables.items():
        if not rows:
            raise ValueError(f"Refusing empty replacement of {name}; inspect coverage first")
        resources.append(dlt.resource(rows, name=name, write_disposition="replace"))
    database_path = Path(database_path or ROOT / ".state/schools.sqlite").resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    destination = dlt.destinations.sqlalchemy(f"sqlite:///{database_path}")
    pipeline = dlt.pipeline(pipeline_name="selected_schools_sqlite", destination=destination,
                            dataset_name="main",
                            pipelines_dir=str(pipelines_dir or ROOT / ".state/dlt"))
    info = pipeline.run(resources)
    info.raise_on_failed_jobs()
    return {"status": "LOADED", "load_ids": list(info.loads_ids),
            "database_path": str(database_path)}


@task(persist_result=False)
def load_duckdb(tables, database_path=None, pipelines_dir=None):
    """Replace only official snapshots; reject partial school scope in an existing DB."""
    import duckdb
    allowed = {'schools', 'statistics', 'survey_observations', 'source_coverage'}
    if not tables or not set(tables).issubset(allowed):
        raise ValueError('Only official data tables may use snapshot replacement')
    resources = []
    for name, rows in tables.items():
        if not rows:
            raise ValueError(f'Refusing empty replacement of {name}; inspect coverage first')
        resources.append(dlt.resource(rows, name=name, write_disposition='replace'))
    database_path = Path(database_path or ROOT / '.state/schools.duckdb').resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        with duckdb.connect(str(database_path), read_only=True) as conn:
            exists = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema='main' AND table_name='schools'").fetchone()[0]
            if exists:
                old = {r[0] for r in conn.execute('SELECT school_unit_code FROM main.schools').fetchall()}
                new = {r['school_unit_code'] for r in tables.get('schools', [])}
                if old != new:
                    raise ValueError('School scope differs; refusing to replace an existing database')
        from datetime import datetime, timezone
        import shutil
        backup = database_path.parent / 'backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.duckdb')
        backup.parent.mkdir(exist_ok=True)
        shutil.copy2(database_path, backup)
    pipeline = dlt.pipeline(pipeline_name='schools_duckdb',
        destination=dlt.destinations.duckdb(str(database_path)), dataset_name='main',
        pipelines_dir=str(pipelines_dir or ROOT / '.state/dlt_duckdb'))
    info = pipeline.run(resources)
    info.raise_on_failed_jobs()
    return {'status': 'LOADED', 'load_ids': list(info.loads_ids), 'database_path': str(database_path)}


@flow(name="selected-school-public-data", persist_result=False, log_prints=True)
def school_data(extract_only=False, replay=None):
    if replay:
        run_dir = Path(replay).resolve()
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    else:
        config = json.loads((ROOT / "config/schools.json").read_text(encoding="utf-8"))
        codes = [s["code"] for s in config["schools"]]
        if not codes or len(set(codes)) != len(codes) or any(len(c) != 8 or not c.isdigit() for c in codes):
            raise ValueError("Need unique eight-digit school-unit codes")
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_dir = ROOT / "outputs/runs" / run_id
        run_dir.mkdir(parents=True)
        manifest = {"run_id": run_id, "selection": config, "sources": []}
        for code in codes:
            for kind, url in endpoints(code).items():
                manifest["sources"].append(retrieve(code, kind, url, str(run_dir)))
                (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    tables = prepare(manifest, run_dir)
    print({"run_directory": str(run_dir), "rows": {k: len(v) for k, v in tables.items()}})
    if not extract_only:
        if any(e["status"] != "FETCHED" for e in manifest["sources"]):
            raise ValueError("Incomplete source coverage; review before replacement load")
        result = load_duckdb(tables)
        (run_dir / "load_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return str(run_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-only", action="store_true")
    parser.add_argument("--replay")
    args = parser.parse_args()
    school_data(extract_only=args.extract_only, replay=args.replay)
