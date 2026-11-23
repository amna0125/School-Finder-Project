"""One-time verified Batch23 checkpoint."""
from pathlib import Path
import csv,json,hashlib,difflib
from collections import Counter
import duckdb
from school_pipeline.approach_migration import E_FIELDS,C_FIELDS,validate_records
from school_pipeline.duckdb_migration import OFFICIAL,q,digest
from outputs.approach_county_review.extract19 import parse
P=Path('outputs/approach_county_review');B=P/'batch23_10schools_20261102'
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=P/'county_progress_20261102_after_batch22.csv';new=P/'county_progress_20261102_after_batch23.csv';assert not new.exists()
loads=[read(p) for p in sorted((B/'loads').glob('*/validation.json'))]
assert len(loads)==2 and [(v['inserted_evidence'],v['inserted_codes']) for v in loads]==[(7,6),(0,0)]
assert all(v['status']=='PASSED' and v['existing_records_preserved'] and v['exact_target_comparison'] and v['exact_staging_comparison'] for v in loads)
assert read(B/'source_hashes.json')=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'sources').iterdir() if p.is_file()}
e=read(B/'Approach_evidence.staged.json');c=read(B/'Approach_codes.staged.json');validate_records(e,c)
logs=list(csv.DictReader((B/'collection_log.csv').open()))
for r in e:
 l=next(x for x in logs if x['school_id']==r['school_id'] and x['selected_url']==r['source_url']);assert r['quoted_text'] in parse(B/l['saved_file'])[0] and r['accessed_date']=='2026-11-02' and r['page_title']==l['page_title']
rows=list(csv.DictReader(old.open()));before={r['school_id']:dict(r) for r in rows};ids={r['school_id'] for r in read(B/'selection.json')};reviews=list(csv.DictReader((B/'review_log.csv').open()));rev={r['school_id']:r for r in reviews}
assert len(rows)==len(before)==762 and len(ids)==len(rev)==10
assert ids=={r['school_id'] for r in sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]}
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 assert {r[0] for r in db.execute('select school_unit_code from schools').fetchall()}==set(before)
 assert {t:digest(db.execute('select * from '+q(t)).fetchall()) for t in OFFICIAL}==loads[0]['official_fingerprints']==loads[1]['official_fingerprints']
 for table,fields,incoming,key in [('approach_evidence',E_FIELDS,e,'evidence_id'),('approach_codes',C_FIELDS,c,'code_id')]:
  actual=db.execute('select '+','.join(map(q,fields))+' from '+table+' where '+key+" like '%b23_%'").fetchall();assert Counter(actual)==Counter(tuple(r[f] for f in fields) for r in incoming)
 assert db.execute('select count(*) from approach_evidence').fetchone()[0]==277 and db.execute('select count(*) from approach_codes').fetchone()[0]==203
for r in rows:
 if r['school_id'] in ids:r.update(review_state=rev[r['school_id']]['outcome'],batch_reference=B.name,collection_status='contextually_reviewed_followups_retained',note=rev[r['school_id']]['unit_scope'])
assert {r['school_id'] for r in rows if r!=before[r['school_id']]}==ids
remaining=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id']);assert len(remaining)==519
with new.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(B/'ledger.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.name,tofile=new.name)))
dump(P/'next_batch_after_batch23.json',remaining[:10])
campaign=read(P/'campaign_200_status.json');dump(B/'campaign_before_batch23.json',campaign)
workflow=(P/'CURRENT_WORKFLOW.md').read_text();(B/'workflow_before_batch23.md').write_text(workflow)
campaign.update(latest_committed_batch=B.name,committed_contextual_reviews=243,latest_ledger=new.name,next_selection='next_batch_after_batch23.json',continuation_note='243 documented outcomes, including unresolved cases;519 pending. Not243 resolved schools.',note='County incomplete; no audited county scope totals.');dump(P/'campaign_200_status.json',campaign)
(P/'CURRENT_WORKFLOW.md').write_text('# Current checkpoint — Batch23, 2026-11-02\n\n243 documented outcomes /519 pending /762 unique IDs;10 rows changed,752 unchanged. Ledger '+new.name+'. Next next_batch_after_batch23.json.\n\nBatch23:6 reviewed schools/6 codes,1 uncertain/no firm code,3 scoped no-clear outcomes;7 evidence. Append hospitable-crab +7/+6; replay abstract-jerboa +0/+0. DB277 evidence/203 codes.22 tests passed; exact staging/target, existing preservation, source quotes/hashes and official fingerprints passed. Git unavailable; ledger diff saved.\n\nFarsta music only selected classes4–9; Magelungen resource placements; Broäng shared rector-area Tåget/MVP7–9; Pershagen developing profile. IES erroneous Karlstad paragraph excluded. Nordic internationally inspired Swedish teaching insufficient for firm international-language code. No audited all-county clear/unclear unit-scope count. Prior caveats and workflow preserved in workflow_before_batch23.md; unresolved follow-ups retained. Do not rerun successful builders/checkpoints. Dashboard deferred.\n')
report=(B/'REPORT.md').read_text();(B/'REPORT.md').write_text(report.replace('Staged; load/checkpoint pending.','Loaded and checkpointed: append+7/+6; replay+0/+0; DB277 evidence/203 codes.22 tests passed. Exact tuples, quotes/hashes, prior preservation and unchanged official fingerprints validated.243 outcomes/519 pending, not resolved-school counts.'))
status=read(B/'batch_status.json');status.update(status='CHECKPOINTED',documented_outcomes=243,pending=519);dump(B/'batch_status.json',status)
for r in reviews:r['load_state']='Loaded; checkpointed; unresolved follow-ups retained'
with (B/'review_log.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=reviews[0]);w.writeheader();w.writerows(reviews)
dump(B/'independent_staging_target_check.json',dict(status='PASSED',exact_quotes=7,source_hashes=True,target_tuples=True,official_fingerprints_unchanged=True))
after=list(csv.DictReader(new.open()));assert len(after)==762 and sum(r['review_state']!='Not yet contextually reviewed' for r in after)==243
assert read(P/'next_batch_after_batch23.json')==remaining[:10]
dump(B/'independent_checkpoint_check.json',dict(status='PASSED',official_ids=762,changed_rows=10,unchanged_rows=752,documented_outcomes=243,pending=519,next_selection_matches=True))
print(json.dumps(dict(status='CHECKPOINTED',documented_outcomes=243,pending=519)))
