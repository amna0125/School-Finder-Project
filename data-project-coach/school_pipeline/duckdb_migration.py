"""Validated SQLite-to-DuckDB migration and idempotent approach batch loading.
Run with --backup PATH --run-dir PATH; no network collection or legacy migration.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

import duckdb
import dlt
from school_pipeline.flow import ROOT, flow
from school_pipeline.approach_migration import E_FIELDS, C_FIELDS, validate_records

DATABASE = ROOT / '.state/schools.duckdb'
OFFICIAL = ['schools', 'statistics', 'survey_observations', 'source_coverage']
BATCHES = ['batch01_followup_20261027', 'batch02_10schools_20261027']


def q(name):
    return '"' + name.replace('"', '""') + '"'


def digest(rows):
    encoded = sorted(json.dumps(list(row), ensure_ascii=False, default=str) for row in rows)
    h = hashlib.sha256()
    for row in encoded:
        h.update((row + '\n').encode())
    return {'rows': len(encoded), 'sha256': h.hexdigest()}


def records(conn, table, fields):
    return [dict(zip(fields, row)) for row in conn.execute(
        f'SELECT {",".join(map(q, fields))} FROM {q(table)}').fetchall()]


def migrate_backup(backup, database):
    """Create a new DB only; compare every column/value, including duplicate rows."""
    database = Path(database)
    if database.exists():
        raise FileExistsError(f'Refusing to replace {database}')
    source = sqlite3.connect(f'file:{Path(backup).resolve()}?mode=ro', uri=True)
    target = duckdb.connect(str(database))
    comparisons = {}
    try:
        if source.execute('pragma integrity_check').fetchall() != [('ok',)]:
            raise ValueError('Backup integrity check failed')
        target.execute('CREATE SCHEMA sqlite_audit')
        target.execute('BEGIN TRANSACTION')
        for (table,) in source.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            schema = 'sqlite_audit' if table.startswith('_dlt_') else 'main'
            columns = source.execute(f'PRAGMA table_info({q(table)})').fetchall()
            types = {'TEXT': 'VARCHAR', 'INTEGER': 'BIGINT', 'BIGINT': 'BIGINT',
                     'REAL': 'DOUBLE', 'DOUBLE': 'DOUBLE', 'BLOB': 'BLOB', 'DATETIME': 'VARCHAR'}
            definitions = []
            for _, name, typ, notnull, default, pk in columns:
                mapped_type = 'VARCHAR' if typ.upper().startswith('VARCHAR') else types.get(typ.upper())
                if mapped_type is None:
                    raise ValueError(f'Unsupported SQLite type {table}.{name}: {typ}')
                definition = f'{q(name)} {mapped_type}'
                if notnull:
                    definition += ' NOT NULL'
                definitions.append(definition)
            if table == 'Approach_evidence':
                definitions += ['PRIMARY KEY(evidence_id)', 'UNIQUE(evidence_id,school_id)']
            if table == 'Approach_codes':
                definitions += ['PRIMARY KEY(code_id)', 'UNIQUE(school_id,category,subcategory)',
                                'FOREIGN KEY(evidence_id,school_id) REFERENCES Approach_evidence(evidence_id,school_id)',
                                "CHECK(review_status IN ('Reviewed','Requires review'))",
                                "CHECK((coding_level='Explicit' AND confidence='High') OR (coding_level='Supported' AND confidence='Medium') OR (coding_level='Unclear' AND confidence='Low'))"]
            dest = f'{schema}.{q(table)}'
            target.execute(f'CREATE TABLE {dest} ({",".join(definitions)})')
            rows = source.execute(f'SELECT * FROM {q(table)}').fetchall()
            # COPY avoids extremely slow row-oriented insertion on this filesystem.
            import csv
            import tempfile
            null_marker = '__SQLITE_NULL_91b30d3c__'
            if any(value == null_marker for row in rows for value in row):
                raise ValueError('NULL marker collision')
            with tempfile.NamedTemporaryFile(mode='w', newline='', dir=database.parent,
                                             suffix='.csv', delete=False) as handle:
                temp_path = Path(handle.name)
                writer = csv.writer(handle)
                writer.writerows([null_marker if value is None else value for value in row] for row in rows)
            try:
                path_sql = str(temp_path.resolve()).replace("'", "''")
                target.execute(f"COPY {dest} FROM '{path_sql}' (FORMAT CSV, HEADER FALSE, NULL '{null_marker}')")
            finally:
                temp_path.unlink()
            actual = target.execute(f'SELECT * FROM {dest}').fetchall()
            if Counter(rows) != Counter(actual):
                raise ValueError(f'Value mismatch: {table}')
            comparisons[table] = {**digest(rows), 'destination': dest, 'exact_values_match': True}
        target.execute('COMMIT')
        target.execute('CHECKPOINT')
    except BaseException:
        try:
            target.execute('ROLLBACK')
        except Exception:
            pass
        raise
    finally:
        source.close()
        target.close()
    return comparisons


def merge_records(existing, incoming, key):
    result = {row[key]: row for row in existing}
    for row in incoming:
        if row[key] in result and result[row[key]] != row:
            raise ValueError(f'Conflicting {key}: {row[key]}')
        result[row[key]] = row
    return list(result.values())


@flow(name='duckdb-migration-and-completed-approach-batches', persist_result=False, log_prints=True)
def migrate_and_load(backup, run_dir, database=None):
    run_dir = Path(run_dir)
    database = Path(database or DATABASE)
    database.parent.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)
    report_path = run_dir / 'migration_validation.json'
    report = {'status': 'STARTED', 'duckdb_version': duckdb.__version__, 'backup': str(backup),
              'database': str(database), 'batches': BATCHES}
    try:
        report['migration'] = migrate_backup(backup, database)
        conn = duckdb.connect(str(database))
        try:
            before = {t: digest(conn.execute(f'SELECT * FROM {q(t)}').fetchall()) for t in OFFICIAL}
            old_e = records(conn, 'Approach_evidence', E_FIELDS)
            old_c = records(conn, 'Approach_codes', C_FIELDS)
            evidence, codes = old_e, old_c
            provenance = []
            for batch in BATCHES:
                folder = ROOT / 'outputs/approach_county_review' / batch
                efile, cfile = folder/'Approach_evidence.staged.json', folder/'Approach_codes.staged.json'
                e, c = json.loads(efile.read_text()), json.loads(cfile.read_text())
                validate_records(e, c)
                evidence = merge_records(evidence, e, 'evidence_id')
                codes = merge_records(codes, c, 'code_id')
                provenance.append({'batch': batch, 'evidence_rows': len(e), 'code_rows': len(c),
                                   'evidence_sha256': hashlib.sha256(efile.read_bytes()).hexdigest(),
                                   'codes_sha256': hashlib.sha256(cfile.read_bytes()).hexdigest(),
                                   'validation': json.loads((folder/'validation.json').read_text())})
            validate_records(evidence, codes)
            school_ids = {r[0] for r in conn.execute('SELECT school_unit_code FROM schools').fetchall()}
            if not all(e['school_id'] in school_ids for e in evidence):
                raise ValueError('Evidence school absent from official directory')
            if any(c['review_status'] != 'Reviewed' or c['coding_level'] == 'Unclear' for c in codes):
                raise ValueError('Firm code snapshot contains unresolved code')
            stage = run_dir/'approach_staging.duckdb'
            pipeline = dlt.pipeline(pipeline_name='approach_duckdb_staging',
                destination=dlt.destinations.duckdb(str(stage)), dataset_name='approach_stage',
                pipelines_dir=str(run_dir/'dlt_staging'))
            info = pipeline.run([dlt.resource(evidence, name='approach_evidence', write_disposition='replace'),
                                 dlt.resource(codes, name='approach_codes', write_disposition='replace')])
            info.raise_on_failed_jobs()
            st = duckdb.connect(str(stage), read_only=True)
            try:
                for name, fields, expected in [('approach_evidence', E_FIELDS, evidence), ('approach_codes', C_FIELDS, codes)]:
                    actual = st.execute(f'SELECT {",".join(map(q,fields))} FROM approach_stage.{name}').fetchall()
                    if Counter(tuple(r[f] for f in fields) for r in expected) != Counter(actual):
                        raise ValueError(f'dlt staging mismatch: {name}')
            finally:
                st.close()
            # Only new rows are inserted. Existing evidence and codes are never replaced.
            old_eids, old_cids = {r['evidence_id'] for r in old_e}, {r['code_id'] for r in old_c}
            conn.execute('BEGIN TRANSACTION')
            try:
                for name, fields, rows, key, old in [('Approach_evidence', E_FIELDS, evidence, 'evidence_id', old_eids),
                                                  ('Approach_codes', C_FIELDS, codes, 'code_id', old_cids)]:
                    new = [tuple(r[f] for f in fields) for r in rows if r[key] not in old]
                    if new:
                        conn.executemany(f'INSERT INTO {q(name)} ({",".join(map(q,fields))}) VALUES ({",".join("?" for _ in fields)})', new)
                if before != {t: digest(conn.execute(f'SELECT * FROM {q(t)}').fetchall()) for t in OFFICIAL}:
                    raise ValueError('Official data changed')
                for name, fields, expected in [('Approach_evidence', E_FIELDS, evidence), ('Approach_codes', C_FIELDS, codes)]:
                    if records(conn, name, fields) != expected:
                        # SQL order is unspecified; compare exact records as multisets.
                        if Counter(tuple(r[f] for f in fields) for r in records(conn,name,fields)) != Counter(tuple(r[f] for f in fields) for r in expected):
                            raise ValueError(f'Live approach mismatch: {name}')
                conn.execute('COMMIT')
            except BaseException:
                conn.execute('ROLLBACK')
                raise
            conn.execute('CHECKPOINT')
            report.update(status='PASSED', official_tables_unchanged=True, pilot_records_preserved=True,
                          before_counts={'evidence':len(old_e),'codes':len(old_c)},
                          final_counts={'evidence':len(evidence),'codes':len(codes)},
                          coded_schools=len({c['school_id'] for c in codes}),
                          staging_load_ids=list(info.loads_ids), batch_provenance=provenance,
                          limitations=['Website claims are not independently verified practice.',
                          'Inherited batch01 provenance and unresolved review outcomes remain in original logs.',
                          'Historical SQLite dlt metadata retained in sqlite_audit, not reused as DuckDB state.'])
        finally:
            conn.close()
    except BaseException as exc:
        report.update(status='FAILED', error=repr(exc))
        raise
    finally:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: report[k] for k in ['status','database','before_counts','final_counts','coded_schools']}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup', required=True)
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args()
    migrate_and_load(args.backup, args.run_dir)
