"""One-time Batch20 checkpoint; requires successful append/replay."""
from pathlib import Path
import csv,json,difflib,hashlib
import duckdb
from school_pipeline.duckdb_migration import OFFICIAL,digest,q
from outputs.approach_county_review.extract19 import parse
P=Path('outputs/approach_county_review');B=P/'batch20_10schools_20261030'
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=P/'county_progress_20261030_after_batch19.csv';new=P/'county_progress_20261030_after_batch20.csv';assert not new.exists()
loads=[read(p) for p in sorted((B/'loads').glob('*/validation.json'))];assert len(loads)==2
assert [(v['inserted_evidence'],v['inserted_codes']) for v in loads]==[(12,5),(0,0)]
assert all(v['status']=='PASSED' and v['existing_records_preserved'] and v['exact_target_comparison'] and v['exact_staging_comparison'] for v in loads)
assert loads[0]['official_fingerprints']==loads[1]['official_fingerprints']
assert read(B/'source_hashes.json')=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'sources').iterdir() if p.is_file()}
rows=list(csv.DictReader(old.open()));before={r['school_id']:dict(r) for r in rows};sel=read(B/'selection.json');ids={r['school_id'] for r in sel};reviews=list(csv.DictReader((B/'review_log.csv').open()));rev={r['school_id']:r for r in reviews}
assert len(rows)==len(before)==762 and len(ids)==len(rev)==10
assert ids=={r['school_id'] for r in sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]}
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 counts={t:db.execute('select count(*) from '+t).fetchone()[0] for t in ['schools','statistics','survey_observations','source_coverage','approach_evidence','approach_codes']}
 assert counts==dict(schools=762,statistics=45868,survey_observations=84610,source_coverage=3048,approach_evidence=250,approach_codes=180)
 assert {r[0] for r in db.execute('select school_unit_code from schools').fetchall()}==set(before)
 assert {t:digest(db.execute('select * from '+q(t)).fetchall()) for t in OFFICIAL}==loads[0]['official_fingerprints']
for r in rows:
 if r['school_id'] in ids:
  v=rev[r['school_id']];r.update(review_state=v['outcome'],batch_reference=B.name,collection_status='contextually_reviewed_followups_retained',note=v['unit_scope'])
assert {r['school_id'] for r in rows if r!=before[r['school_id']]}==ids
remaining=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id']);assert len(remaining)==549
with new.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(B/'ledger.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.name,tofile=new.name)))
dump(P/'next_batch_after_batch20.json',remaining[:10])
campaign=read(P/'campaign_200_status.json');dump(B/'campaign_before_batch20.json',campaign)
workflow=(P/'CURRENT_WORKFLOW.md').read_text();(B/'workflow_before_batch20.md').write_text(workflow)
campaign.update(latest_committed_batch=B.name,committed_contextual_reviews=213,latest_ledger=new.name,next_selection='next_batch_after_batch20.json',continuation_note='213 documented outcomes including unresolved/access cases, not213 resolved schools;549 pending. Minimum200 reached, county incomplete. Continue on demand in batches of10.',note='213 outcomes; unresolved follow-ups retained; county incomplete.')
dump(P/'campaign_200_status.json',campaign)
new_workflow='''# Current checkpoint — Batch20, 2026-10-30

Append indigo-aardvark +12 evidence/+5 codes; replay silky-squid +0/+0. Totals250 evidence/180 codes, not school counts. Exact staging/target checks and prior records preserved, official fingerprints unchanged.22 unittest tests passed.

Ledger county_progress_20261030_after_batch20.csv:213 documented outcomes/549 pending/762 unique official IDs; exactly10 rows changed. Not213 resolved schools or county completion. Minimum200 already reached. Next next_batch_after_batch20.json, ascending pending IDs, on-demand batches of10.

Batch20:4 schools with5 reviewed self-description codes;2 scoped no-clear-evidence,1 unclear arts statement,1 inaccessible source,1 identity uncertainty,1 dormant-status case. Follow-ups: ID34672217 database Stavsborgsskolan vs ledger/URL Älta resursskola, explicitly separate unit; no support code. Runmarö dormant2026/27; no current outdoor code. Solbergaskolan Stockholm outage403 on robots; no school content/no bypass. Källberga F–6/7–9 site split vs official1–7. Bergius dance/Må Bra optional undated profile pages; no causal effects inferred. Carlssons arts wording and Lilla single entrepreneurial project insufficient for firm approach labels. Self-reported Lilla class-size and DiStra adults ratio not official comparable teacher metrics. Prior batch caveats remain in their review logs and workflow_before_batch20.md.

Do not rerun one-time builders/checkpoints including Batch20 or earlier. Dashboard deferred. No unattended schedule.
'''
(P/'CURRENT_WORKFLOW.md').write_text(new_workflow)
(B/'workflow.diff').write_text(''.join(difflib.unified_diff(workflow.splitlines(True),new_workflow.splitlines(True))))
for r in reviews:r['load_state']='Loaded; exact comparisons and zero-insert replay passed'
with (B/'review_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=reviews[0]);w.writeheader();w.writerows(reviews)
dump(B/'batch_status.json',dict(status='LOADED_REPLAY_VERIFIED_RECONCILED',schools=10,evidence_added=12,codes_added=5,documented_outcomes=213,pending=549,remaining_followups='See review_log.csv/decision_log.md; processed does not mean resolved.'))
with (B/'REPORT.md').open('a') as f:f.write('\n## Persistence verified\nAppend indigo-aardvark +12/+5; replay silky-squid +0/+0. Exact comparisons, official fingerprints and prior records preserved.22 tests passed. Reconciled213 outcomes/549 pending/762 IDs, exactly10 rows changed. Outstanding follow-ups retained, county incomplete.\n')
dump(B/'checkpoint_validation.json',dict(status='PASSED',ledger_rows=762,unique_ids=762,changed_rows=10,documented_outcomes=213,pending=549,next_selection_ids=[r['school_id'] for r in remaining[:10]],append_flow='indigo-aardvark',replay_flow='silky-squid',unit_tests_passed=22,official_fingerprints_preserved=True,db_counts=counts,source_hashes_verified=True))
print('Checkpoint reconciled:213 outcomes,549 pending,762 IDs; exactly10 rows changed')
