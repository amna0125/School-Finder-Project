"""County-wide runner reusing the pilot's retrieval, transforms and dlt destination."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from prefect import flow, task
from school_pipeline.flow import ROOT, REGISTER, endpoints, retrieve, prepare, load_duckdb

MUNICIPALITIES = ('0114','0115','0117','0120','0123','0125','0126','0127','0128',
                  '0136','0138','0139','0140','0160','0162','0163','0180','0181',
                  '0182','0183','0184','0186','0187','0188','0191','0192')


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)


@task(retries=2, retry_delay_seconds=5, persist_result=False)
def discover(run_dir):
    schools = {}
    sources = []
    for municipality in MUNICIPALITIES:
        url = REGISTER + '?' + urlencode({'school_type': 'GR', 'status': 'AKTIV',
                                         'municipality_code': municipality})
        with urlopen(Request(url, headers={'Accept': 'application/json',
                     'User-Agent': 'SchoolCourseProject/0.1 (public county data)'}), timeout=45) as response:
            payload = json.load(response)
        rows = payload['data']['attributes']
        if not isinstance(rows, list):
            raise ValueError('Unexpected directory response')
        save(Path(run_dir) / f'discovery_{municipality}.json', payload)
        sources.append({'municipality_code': municipality, 'url': url,
                        'retrieved_at': datetime.now(timezone.utc).isoformat(), 'rows': len(rows)})
        for row in rows:
            code = row['schoolUnitCode']
            if len(code) != 8 or not code.isdigit() or row['status'] != 'AKTIV':
                raise ValueError('Invalid directory entry')
            if code in schools:
                raise ValueError('School appears in multiple municipalities')
            schools[code] = {'code': code, 'name': row['name'], 'municipality_code': municipality}
        time.sleep(0.3)
    if not schools:
        raise ValueError('Empty county discovery')
    return {'scope': 'Active GR school units in all 26 Stockholm County municipalities',
            'discovery_sources': sources, 'schools': sorted(schools.values(), key=lambda s: s['code'])}


def collect_one(code, kind, url, run_dir):
    for attempt in range(3):
        try:
            return retrieve.fn(code, kind, url, run_dir)
        except Exception as exc:
            if attempt == 2:
                return {'code': code, 'kind': kind, 'url': url, 'status': 'FAILED',
                        'error_type': type(exc).__name__,
                        'retrieved_at': datetime.now(timezone.utc).isoformat()}
            time.sleep(5 * (attempt + 1))


@task(persist_result=False)
def collect(manifest, run_dir):
    # Bounded concurrency; each worker retains retrieval pacing and retry limits.
    existing = {(e['code'], e['kind']): e for e in manifest['sources'] if e['status'] != 'FAILED'}
    jobs = [(s['code'], kind, url) for s in manifest['selection']['schools']
            for kind, url in endpoints(s['code']).items() if (s['code'], kind) not in existing]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(collect_one, code, kind, url, str(run_dir)) for code, kind, url in jobs]
        for future in as_completed(futures):
            entry = future.result()
            existing[(entry['code'], entry['kind'])] = entry
            manifest['sources'] = sorted(existing.values(), key=lambda e: (e['code'], e['kind']))
            save(run_dir / 'manifest.json', manifest)
            if len(existing) % 100 == 0:
                print(f'Checkpoint: {len(existing)} / {len(manifest["selection"]["schools"]) * 4} sources', flush=True)
    return manifest


def validate_manifest(manifest):
    expected = {(s['code'], kind) for s in manifest['selection']['schools'] for kind in endpoints(s['code'])}
    actual = {(e['code'], e['kind']) for e in manifest['sources']}
    if expected != actual or len(actual) != len(manifest['sources']):
        raise ValueError('Incomplete or duplicate source manifest')
    if any(e['status'] not in {'FETCHED', 'UNAVAILABLE'} for e in manifest['sources']):
        raise ValueError('Failed sources remain; resume before loading')
    if any(e['kind'] == 'register' and e['status'] != 'FETCHED' for e in manifest['sources']):
        raise ValueError('Missing register identity; review before loading')


@flow(name='stockholm-county-public-school-data', persist_result=False, log_prints=True)
def county_data(resume=None, extract_only=False):
    if resume:
        run_dir = Path(resume).resolve()
        manifest = json.loads((run_dir / 'manifest.json').read_text())
    else:
        run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        run_dir = ROOT / 'outputs/runs' / ('county_' + run_id)
        run_dir.mkdir(parents=True)
        manifest = {'run_id': run_id, 'selection': discover(str(run_dir)), 'sources': []}
        save(run_dir / 'manifest.json', manifest)
    print(f'Run directory: {run_dir}; schools: {len(manifest["selection"]["schools"])}', flush=True)
    manifest = collect(manifest, run_dir)
    validate_manifest(manifest)
    tables = prepare(manifest, run_dir)
    if len(tables['schools']) != len(manifest['selection']['schools']):
        raise ValueError('School count mismatch')
    if not extract_only:
        result = load_duckdb(tables)  # Loader backs up DuckDB before replacement.
        save(run_dir / 'load_result.json', result)
        print(result, flush=True)
    print(json.loads((run_dir / 'coverage.json').read_text()), flush=True)
    return str(run_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume')
    parser.add_argument('--extract-only', action='store_true')
    args = parser.parse_args()
    county_data(args.resume, args.extract_only)
