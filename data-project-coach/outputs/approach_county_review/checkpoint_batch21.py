"""One-time Batch21 checkpoint, following validated append and replay."""
from pathlib import Path
import csv,json,hashlib,difflib
import duckdb
from school_pipeline.duckdb_migration import OFFICIAL,digest,q
P=Path('outputs/approach_county_review');B=P/'batch21_10schools_20261030'
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=P/'county_progress_20261030_after_batch20.csv';new=P/'county_progress_20261030_after_batch21.csv';assert not new.exists()
loads=[read(p) for p in sorted((B/'loads').glob('*/validation.json'))];assert len(loads)==2
assert [(v['inserted_evidence'],v['inserted_codes']) for v in loads]==[(9,9),(0,0)]
assert all(v['status']=='PASSED' and v['existing_records_preserved'] and v['exact_target_comparison'] and v['exact_staging_comparison'] for v in loads)
assert read(B/'independent_staging_target_check.json')['status']=='PASSED'
assert read(B/'source_hashes.json')=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'sources').iterdir() if p.is_file()}
rows=list(csv.DictReader(old.open()));before={r['school_id']:dict(r) for r in rows};ids={r['school_id'] for r in read(B/'selection.json')};reviews=list(csv.DictReader((B/'review_log.csv').open()));rev={r['school_id']:r for r in reviews}
assert len(rows)==len(before)==762 and len(ids)==len(rev)==10
assert ids=={r['school_id'] for r in sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]}
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 counts={t:db.execute('select count(*) from '+t).fetchone()[0] for t in ['schools','statistics','survey_observations','source_coverage','approach_evidence','approach_codes']}
 assert counts==dict(schools=762,statistics=45868,survey_observations=84610,source_coverage=3048,approach_evidence=259,approach_codes=189)
 assert {r[0] for r in db.execute('select school_unit_code from schools').fetchall()}==set(before)
 assert {t:digest(db.execute('select * from '+q(t)).fetchall()) for t in OFFICIAL}==loads[0]['official_fingerprints']==loads[1]['official_fingerprints']
for r in rows:
 if r['school_id'] in ids:
  v=rev[r['school_id']];r.update(review_state=v['outcome'],batch_reference=B.name,collection_status='contextually_reviewed_followups_retained',note=v['unit_scope'])
assert {r['school_id'] for r in rows if r!=before[r['school_id']]}==ids
remaining=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id']);assert len(remaining)==539
with new.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(B/'ledger.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.name,tofile=new.name)))
dump(P/'next_batch_after_batch21.json',remaining[:10])
campaign=read(P/'campaign_200_status.json');dump(B/'campaign_before_batch21.json',campaign)
workflow=(P/'CURRENT_WORKFLOW.md').read_text();(B/'workflow_before_batch21.md').write_text(workflow)
campaign.update(latest_committed_batch=B.name,committed_contextual_reviews=223,latest_ledger=new.name,next_selection='next_batch_after_batch21.json',continuation_note='223 documented outcomes including unresolved/access cases, not223 resolved schools;539 pending. Minimum200 reached, county incomplete. Continue on demand in batches of10.',note='223 outcomes; unresolved follow-ups retained; county incomplete.')
dump(P/'campaign_200_status.json',campaign)
new_workflow='''# Current checkpoint — Batch21, 2026-10-30

Append jasper-centipede +9 evidence/+9 codes; replay holistic-herring +0/+0. Totals259 evidence/189 codes, not school counts. Exact staging/target checks and prior records preserved; official fingerprints unchanged.22 unittest tests passed (tests directory); initial wrong discovery path ran0 and is not counted as a pass. Independent quotation/hash/target check passed.

Ledger county_progress_20261030_after_batch21.csv:223 documented outcomes/539 pending/762 unique official IDs, exactly10 rows changed. Not223 resolved schools or county completion. Minimum200 already reached. Next next_batch_after_batch21.json; ascending pending IDs, on-demand batches of10.

Batch21:6 schools with9 reviewed self-description codes;3 scoped no-clear-evidence;1 uncertain language/health emphasis without firm code.9 evidence rows. Reviewed claims are not independently verified practice. Tunaskolan registered404 but current municipal200; Vällingby/Högland now accessible without rewriting historical access records. Kottla verified official ID36276828,7–9,Lidingö; DB name Futuraskolan AB retained. Swedish curriculum plus IMYC, not separate International School of Stockholm permit/curriculum. F-class vs official1–9/1–6 differences and shared preschool/anpassad-school scope exclusions retained. Unverified pupil/group/staff and PE-comparator claims not official comparable metrics. See collection_log.csv, review_log.csv and decision_log.md.

Earlier caveats remain in workflow_before_batch21.md and previous batch logs, including Solbergaskolan403, Älta/Stavsborg identity mismatch, Runmarö dormant status and earlier reconciliation needs. Processing is not resolving every follow-up.

Do not rerun one-time builders/checkpoints including Batch21 or earlier. Dashboard deferred. No unattended schedule.
'''
(P/'CURRENT_WORKFLOW.md').write_text(new_workflow)
(B/'workflow.diff').write_text(''.join(difflib.unified_diff(workflow.splitlines(True),new_workflow.splitlines(True))))
for r in reviews:r['load_state']='Loaded; replay verified; ledger reconciled'
with (B/'review_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=reviews[0]);w.writeheader();w.writerows(reviews)
dump(B/'batch_status.json',dict(status='LOADED_REPLAY_VERIFIED_RECONCILED',schools=10,evidence=9,codes=9,date='2026-10-30',documented_outcomes=223,pending=539))
with (B/'REPORT.md').open('a') as f:f.write('\n## Persistence verified\nAppend jasper-centipede +9/+9; replay holistic-herring +0/+0.22 tests passed; independent quote/hash/target check passed. Official fingerprints and prior records preserved.223 documented outcomes/539 pending/762 IDs, exactly10 ledger rows changed. Follow-ups retained; county incomplete.\n')
dump(B/'checkpoint_validation.json',dict(status='PASSED',ledger_rows=762,unique_ids=762,changed_rows=10,documented_outcomes=223,pending=539,next_selection_ids=[r['school_id'] for r in remaining[:10]],append_flow='jasper-centipede',replay_flow='holistic-herring',unit_tests_passed=22,official_fingerprints_preserved=True,db_counts=counts,source_hashes_verified=True))
print('Checkpoint reconciled:223 outcomes/539 pending/762 IDs; exactly10 changed.')
