"""Offline Prefect + dlt smoke test using saved public-source fixtures.
Run: python3 -m school_pipeline.smoke_sqlite
Does not populate the production school database or fetch live sources.
"""
import json
from pathlib import Path
import sqlite3
from school_pipeline.flow import ROOT, load_sqlite, flow
from school_pipeline.transform import school, statistics, surveys


@flow(name='sqlite-offline-smoke', persist_result=False, log_prints=True)
def smoke(orchestrated=True):
    def fixture(name):
        return json.loads((ROOT / 'outputs' / name).read_text(encoding='utf-8'))

    # Original retrieval metadata is not reconstructed or invented for these fixtures.
    provenance = {'source_url': 'offline-test-fixture', 'retrieved_at': 'unknown-fixture-date',
                  'response_sha256': 'not-asserted-in-smoke-test'}
    code = '98760751'
    tables = {
        'schools': [school(fixture('pilot_register_kristofferskolan.json'), code, provenance)],
        'statistics': statistics(fixture('pilot_statistics_kristofferskolan.json'), code, provenance),
        'survey_observations': (
            surveys(fixture('probe_parent_survey.json'), code, 'parents', provenance)
            + surveys(fixture('probe_pupil_survey.json'), code, 'pupils', provenance)),
        'source_coverage': [{'code': code, 'status': 'OFFLINE_FIXTURES_NOT_LIVE_EXTRACTION'}],
    }
    database = ROOT / '.state/smoke/schools.sqlite'
    loader = load_sqlite if orchestrated else load_sqlite.fn
    for _ in range(2):
        result = loader(tables, database, ROOT / '.state/smoke/dlt')
    with sqlite3.connect(database) as conn:
        names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        counts = {}
        for logical_name, rows in tables.items():
            physical_name = next(n for n in names if n == logical_name or n.endswith('__' + logical_name))
            counts[logical_name] = conn.execute(f'SELECT COUNT(*) FROM "{physical_name}"').fetchone()[0]
            assert counts[logical_name] == len(rows), (logical_name, counts[logical_name], len(rows))
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    report = {'scope': 'offline saved-fixture replay, not live extraction',
              'status': 'PASSED', 'prefect_orchestrated': orchestrated,
              'loads': 2, 'row_counts': counts,
              'database_path': str(database.relative_to(ROOT)), 'load_status': result['status']}
    (ROOT / 'outputs/sqlite_smoke_result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(report)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--direct', action='store_true', help='Test dlt only; no Prefect server')
    args = parser.parse_args()
    if args.direct:
        smoke.fn(orchestrated=False)
    else:
        smoke()
