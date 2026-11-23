"""Append validated approach batches via native dlt staging and atomic DuckDB inserts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import duckdb
import dlt
from prefect import flow
from school_pipeline.approach_migration import E_FIELDS, C_FIELDS, validate_records
from school_pipeline.duckdb_migration import DATABASE, OFFICIAL, q, digest, records, merge_records

@flow(name='append-reviewed-approach-batch', persist_result=False, log_prints=True)
def append_batch(batch, database=None):
    batch=Path(batch).resolve(); database=Path(database or DATABASE).resolve()
    incoming_e=json.loads((batch/'Approach_evidence.staged.json').read_text())
    incoming_c=json.loads((batch/'Approach_codes.staged.json').read_text())
    validate_records(incoming_e,incoming_c)
    if not incoming_e or not incoming_c:
        raise ValueError('Empty batch not accepted by this loader')
    if any(c['review_status']!='Reviewed' or c['coding_level']=='Unclear' for c in incoming_c):
        raise ValueError('Unresolved firm code')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run=batch/'loads'/stamp; run.mkdir(parents=True)
    # Fail on locks rather than deleting sidecars or killing processes.
    conn=duckdb.connect(str(database))
    try:
        conn.execute('CHECKPOINT')
        backup=run/'before.duckdb';shutil.copy2(database,backup)
        before={t:digest(conn.execute(f'SELECT * FROM {q(t)}').fetchall()) for t in OFFICIAL}
        old_e=records(conn,'Approach_evidence',E_FIELDS);old_c=records(conn,'Approach_codes',C_FIELDS)
        evidence=merge_records(old_e,incoming_e,'evidence_id');codes=merge_records(old_c,incoming_c,'code_id')
        validate_records(evidence,codes)
        ids={r[0] for r in conn.execute('SELECT school_unit_code FROM schools').fetchall()}
        if not all(e['school_id'] in ids for e in evidence):raise ValueError('Unknown school ID')
        stage=run/'stage.duckdb'
        p=dlt.pipeline(pipeline_name='append_approach_stage',destination=dlt.destinations.duckdb(str(stage)),dataset_name='approach_stage',pipelines_dir=str(run/'dlt'))
        info=p.run([dlt.resource(incoming_e,name='approach_evidence',write_disposition='append'),dlt.resource(incoming_c,name='approach_codes',write_disposition='append')]);info.raise_on_failed_jobs()
        st=duckdb.connect(str(stage),read_only=True)
        try:
            for name,fields,expected in [('approach_evidence',E_FIELDS,incoming_e),('approach_codes',C_FIELDS,incoming_c)]:
                actual=st.execute(f'SELECT {",".join(map(q,fields))} FROM approach_stage.{name}').fetchall()
                if Counter(actual)!=Counter(tuple(r[f] for f in fields) for r in expected):raise ValueError('Staging mismatch')
        finally:st.close()
        conn.execute('BEGIN TRANSACTION')
        try:
            for name,fields,rows,key,old in [('Approach_evidence',E_FIELDS,evidence,'evidence_id',{r['evidence_id'] for r in old_e}),('Approach_codes',C_FIELDS,codes,'code_id',{r['code_id'] for r in old_c})]:
                new=[tuple(r[f] for f in fields) for r in rows if r[key] not in old]
                if new:conn.executemany(f'INSERT INTO {q(name)} ({",".join(map(q,fields))}) VALUES ({",".join("?" for _ in fields)})',new)
                actual=records(conn,name,fields)
                if Counter(tuple(r[f] for f in fields) for r in actual)!=Counter(tuple(r[f] for f in fields) for r in rows):raise ValueError('Target mismatch')
            if before!={t:digest(conn.execute(f'SELECT * FROM {q(t)}').fetchall()) for t in OFFICIAL}:raise ValueError('Official data changed')
            conn.execute('COMMIT')
        except BaseException:
            conn.execute('ROLLBACK');raise
        conn.execute('CHECKPOINT')
        report=dict(status='PASSED',database=str(database),duckdb_version=duckdb.__version__,backup=str(backup),official_fingerprints=before,evidence_total=len(evidence),codes_total=len(codes),inserted_evidence=len(evidence)-len(old_e),inserted_codes=len(codes)-len(old_c),exact_staging_comparison=True,exact_target_comparison=True,existing_records_preserved=True)
        (run/'validation.json').write_text(json.dumps(report,indent=2));(batch/'load_validation.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report,indent=2));return report
    finally:conn.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--database');a=p.parse_args();append_batch(a.batch,a.database)
