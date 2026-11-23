"""One-time Batch18 checkpoint; run only after validated append/replay."""
from pathlib import Path
import csv,difflib,json
P=Path('outputs/approach_county_review');B=P/'batch18_10schools_20261030'
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
assert not (P/'county_progress_20261030_after_batch18.csv').exists()
loads=[read(p) for p in sorted((B/'loads').glob('*/validation.json'))];assert len(loads)==2
assert [(x['inserted_evidence'],x['inserted_codes']) for x in loads]==[(13,8),(0,0)]
assert all(x['status']=='PASSED' and x['existing_records_preserved'] and x['exact_target_comparison'] and x['exact_staging_comparison'] for x in loads)
old=P/'county_progress_20261030_after_batch17.csv';rows=list(csv.DictReader(old.open()));sel=read(B/'selection.json');ids={x['school_id'] for x in sel};reviews=list(csv.DictReader((B/'review_log.csv').open()));rev={x['school_id']:x for x in reviews};before={x['school_id']:dict(x) for x in rows}
assert len(rows)==762 and len(before)==762 and len(ids)==10
pending=[x for x in rows if x['review_state']=='Not yet contextually reviewed'];assert ids=={x['school_id'] for x in sorted(pending,key=lambda x:x['school_id'])[:10]}
for x in rows:
 if x['school_id'] in ids:
  r=rev[x['school_id']];x.update(review_state=r['outcome'],batch_reference=B.name,collection_status='contextually_reviewed_followups_retained',note=r['unit_scope']+' '+r['follow_up'])
assert {x['school_id'] for x in rows if x!=before[x['school_id']]}==ids
new=P/'county_progress_20261030_after_batch18.csv'
with new.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(B/'ledger.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.name,tofile=new.name)))
remaining=sorted([x for x in rows if x['review_state']=='Not yet contextually reviewed'],key=lambda x:x['school_id']);assert len(remaining)==569
dump(P/'next_batch_after_batch18.json',remaining[:10])
campaign=read(P/'campaign_200_status.json');dump(B/'campaign_before_batch18.json',campaign)
campaign.update(latest_committed_batch=B.name,committed_contextual_reviews=193,campaign_status='CHECKPOINTED_TARGET_NOT_REACHED',target_reached=False,latest_ledger=new.name,remaining_minimum=7,remaining_whole_batches_to_203=1,next_selection='next_batch_after_batch18.json',continuation_note='193 documented outcomes including unresolved cases, not193 resolved schools. Batch18 loaded and replay verified; target200 not reached.',target_remaining_minimum=7,planned_batches_remaining=1,note='193 documented outcomes, not resolved schools. One ten-school batch to203.')
dump(P/'campaign_200_status.json',campaign)
workflow=P/'CURRENT_WORKFLOW.md';(B/'workflow_before_batch18.md').write_text(workflow.read_text())
workflow.write_text('''# Current checkpoint — Batch18,2026-10-30

Batch18 loaded (Prefect khaki-foxhound), replay verified (pistachio-sloth): +13 evidence/+8 codes; totals226/171. Exact staging/target comparisons passed; official fingerprints and prior records preserved.22 unittest tests passed.

Ledger: county_progress_20261030_after_batch18.csv;193 documented outcomes,569 pending,762 unique IDs. Target200 not reached; one ten-school batch to203. Next: next_batch_after_batch18.json, ascending official IDs. Processing is not full resolution.

Batch18 follow-ups: Stockholm robots control-byte uncertainty; Enhagen official/ledger name difference; Mörtvik outdoor evidence unclear; Munsö SAM/CPS scope caveat. Robots checked after initial fetches; legal terms not exhaustively reviewed. Prior batch follow-ups preserved in their artifacts.

Do not rerun one-time builders/finalizers, including build_batch18.py and checkpoint_batch18.py. Dashboard deferred.
''')
for x in reviews:x['load_state']='Loaded; exact comparison and zero-insert replay passed'
with (B/'review_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=reviews[0].keys());w.writeheader();w.writerows(reviews)
dump(B/'batch_status.json',dict(status='LOADED_AND_REPLAY_VERIFIED',schools=10,evidence_added=13,codes_added=8,documented_outcomes=193,pending=569,remaining_followups='See review_log.csv and decision_log.md; processed is not fully resolved'))
with (B/'REPORT.md').open('a') as f:f.write('\n## Persistence verified\nAppend khaki-foxhound added13/8; replay pistachio-sloth added0/0. Totals226 evidence/171 codes. Exact comparisons and preservation checks passed;22 tests passed. Ledger193 outcomes/569 pending; exactly10 rows changed. Target200 not reached. Source claims remain unverified; Mörtvik uncertainty and other scope/policy caveats retained.\n')
dump(B/'checkpoint_validation.json',dict(status='PASSED',ledger_rows=762,unique_ids=762,changed_rows=10,documented_outcomes=193,pending=569,next_selection_ids=[x['school_id'] for x in remaining[:10]],append_flow='khaki-foxhound',replay_flow='pistachio-sloth',unit_tests_passed=22,official_fingerprints_preserved=True))
print('Checkpoint saved:193 outcomes,569 pending, exactly10 changed rows; next IDs', [x['school_id'] for x in remaining[:10]])
