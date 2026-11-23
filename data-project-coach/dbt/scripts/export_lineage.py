"""Write web/public/data/lineage.json from dbt's manifest and run results.

Run after `dbt build --profiles-dir .` from the dbt folder:
    python scripts/export_lineage.py
The website's Data pipeline page draws the lineage and test results from this file.
"""
import json, os, pathlib, datetime
import duckdb

HERE = pathlib.Path(__file__).resolve().parent.parent          # dbt/
target = HERE / "target"
out = pathlib.Path(os.environ.get("DBT_EXPORT_DIR", HERE.parent / "web" / "public" / "data"))
if not out.is_absolute():
    out = (HERE / out).resolve()
manifest = json.loads((target / "manifest.json").read_text())
runs = json.loads((target / "run_results.json").read_text())
status = {r["unique_id"]: r["status"] for r in runs["results"]}

warehouse = os.environ.get("DBT_WAREHOUSE", str(HERE.parent / ".state" / "warehouse.duckdb"))
con = duckdb.connect(warehouse, read_only=True)
raw = os.environ.get("DBT_RAW_DB", str(HERE.parent / ".state" / "schools.duckdb"))
con.execute(f"attach '{raw}' as raw (read_only)")

def rows(sql):
    try:
        return int(con.execute(sql).fetchone()[0])
    except Exception:
        return None

nodes = []
for uid, n in manifest["nodes"].items():
    if n["resource_type"] not in ("model", "seed"):
        continue
    layer = "seed" if n["resource_type"] == "seed" else n["fqn"][1]
    if layer == "gold":
        loc = (out / f"{n['name']}.parquet").as_posix()
        count = rows(f"select count(*) from read_parquet('{loc}')")
    else:
        count = rows(f"select count(*) from {n['schema']}.{n['name']}")
    nodes.append(dict(
        id=uid, name=n["name"], layer=layer, kind=n["resource_type"],
        materialized=n["config"].get("materialized"),
        description=n.get("description", ""),
        depends_on=list(n.get("depends_on", {}).get("nodes", [])),
        columns=len(n.get("columns", {})), rows=count, status=status.get(uid),
        sql=n.get("raw_code", "") if n["resource_type"] == "model" else "",
        path=n.get("original_file_path"),
    ))
for uid, s in manifest["sources"].items():
    count = rows(f"select count(*) from {s['relation_name']}") if s["source_name"] == "raw" else None
    nodes.append(dict(id=uid, name=s["name"], layer="source", kind="source", materialized=None,
                      description=s.get("description") or s.get("source_description", ""),
                      depends_on=[], columns=0, rows=count, status=None, sql="",
                      path=s.get("original_file_path"), source=s["source_name"]))

tests = []
for uid, t in manifest["nodes"].items():
    if t["resource_type"] != "test":
        continue
    meta = t.get("test_metadata") or {}
    tests.append(dict(name=t["name"], kind=meta.get("name", "singular"), column=t.get("column_name"),
                      on=list(t.get("depends_on", {}).get("nodes", [])), status=status.get(uid)))

doc = dict(generated=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           dbt_version=manifest["metadata"]["dbt_version"], adapter=manifest["metadata"].get("adapter_type"),
           elapsed=runs.get("elapsed_time"), nodes=sorted(nodes, key=lambda n: n["name"]), tests=tests)
(out / "lineage.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
print(f"lineage.json: {len(nodes)} nodes, {len(tests)} tests ->", out / "lineage.json")
