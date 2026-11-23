"""One-time Batch22 checkpoint after validated load/replay; do not rerun."""
from pathlib import Path
import json,csv,hashlib,difflib
from collections import Counter
import duckdb
from school_pipeline.approach_migration import E_FIELDS,C_FIELDS,validate_records
from school_pipeline.duckdb_migration import OFFICIAL,q,digest
from outputs.approach_county_review.extract19 import parse
P=Path('outputs/approach_county_review');B=P/'batch22_10schools_20261102'
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=P/'county_progress_20261030_after_batch21.csv';new=P/'county_progress_20261102_after_batch22.csv';assert not new.exists()
loads=[read(p) for p in sorted((B/'loads').glob('*/validation.json'))]
assert len(loads)==2 and [(v['inserted_evidence'],v['inserted_codes']) for v in loads]==[(11,8),(0,0)]
assert all(v['status']=='PASSED' and v['existing_records_preserved'] and v['exact_target_comparison'] and v['exact_staging_comparison'] for v in loads)
assert read(B/'source_hashes.json')=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'sources').iterdir() if p.is_file()}
e=read(B/'Approach_evidence.staged.json');c=read(B/'Approach_codes.staged.json');validate_records(e,c)
logs=list(csv.DictReader((B/'collection_log.csv').open()))
for r in e:
 l=next(x for x in logs if x['school_id']==r['school_id'] and x['selected_url']==r['source_url']);p=B/l['saved_file'];t=p.read_text() if p.suffix=='.txt' else parse(p)[0]
 assert r['quoted_text'] in t and r['accessed_date']=='2026-11-02' and r['page_title']==l['page_title']
rows=list(csv.DictReader(old.open()));before={r['school_id']:dict(r) for r in rows};selection=read(B/'selection.json');ids={r['school_id'] for r in selection};reviews=list(csv.DictReader((B/'review_log.csv').open()));rev={r['school_id']:r for r in reviews}
assert len(rows)==len(before)==762 and len(ids)==len(rev)==10
assert ids=={r['school_id'] for r in sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]}
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 assert {r[0] for r in db.execute('select school_unit_code from schools').fetchall()}==set(before)
 assert {t:digest(db.execute('select * from '+q(t)).fetchall()) for t in OFFICIAL}==loads[0]['official_fingerprints']==loads[1]['official_fingerprints']
 for table,fields,incoming,key in [('approach_evidence',E_FIELDS,e,'evidence_id'),('approach_codes',C_FIELDS,c,'code_id')]:
  actual=db.execute('select '+','.join(map(q,fields))+' from '+table+' where '+key+" like '%b22_%'").fetchall()
  assert Counter(actual)==Counter(tuple(r[f] for f in fields) for r in incoming)
 assert db.execute('select count(*) from approach_evidence').fetchone()[0]==270
 assert db.execute('select count(*) from approach_codes').fetchone()[0]==197
for r in rows:
 if r['school_id'] in ids:r.update(review_state=rev[r['school_id']]['outcome'],batch_reference=B.name,collection_status='contextually_reviewed_followups_retained',note=rev[r['school_id']]['unit_scope'])
assert {r['school_id'] for r in rows if r!=before[r['school_id']]}==ids
remaining=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id']);assert len(remaining)==529
with new.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(B/'ledger.diff').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.name,tofile=new.name)))
dump(P/'next_batch_after_batch22.json',remaining[:10])
campaign=read(P/'campaign_200_status.json');dump(B/'campaign_before_batch22.json',campaign)
workflow=(P/'CURRENT_WORKFLOW.md').read_text();(B/'workflow_before_batch22.md').write_text(workflow)
campaign.update(latest_committed_batch=B.name,committed_contextual_reviews=233,latest_ledger=new.name,next_selection='next_batch_after_batch22.json',continuation_note='233 documented outcomes including unresolved/access cases, not233 resolved schools;529 pending. Continue on demand in batches of10.',note='233 outcomes; unresolved follow-ups retained; county incomplete.')
dump(P/'campaign_200_status.json',campaign)
(P/'CURRENT_WORKFLOW.md').write_text('''# Current checkpoint — Batch22, 2026-11-02

233 documented outcomes /529 pending /762 unique official IDs. Exactly10 selected ledger rows changed;752 untouched. Not233 resolved schools or county completion. Next next_batch_after_batch22.json, ascending pending IDs. Ledger county_progress_20261102_after_batch22.csv.

Batch22:6 schools with8 reviewed self-description codes;3 uncertain evidence/no firm code;1 scoped no-clear-evidence outcome.11 evidence rows. DB totals270 evidence/197 codes, not school counts. Append formidable-squid +11/+8; replay garnet-doberman +0/+0. Backups in batch22 loads. Exact staging/target comparison, prior record preservation, source quote/hash checks and official fingerprints passed.22 tests passed. Git diff unavailable: not a Git repository; ledger diff saved separately.

Kumla music profile currently years4–7 at Kumla in2026/27; years8–9 at Nyboda. Akalla RSU and Rinkeby support groups restricted to placements, not whole pupil populations. Gåshaga official-directory campus label vs DB Futuraskolan AB preserved; F-class and official grade-range differences retained. Iljansboda stale curriculum and Stenmo/Kista insufficient profile evidence remain uncertain. Prior inaccessible Stockholm/Huddinge pages now200 without overwriting historical failures. Public self-descriptions, not verified practice. No all-county clear/unclear unit-scope count has been audited; approach-outcome totals must not substitute for scope counts.

Earlier caveats preserved in workflow_before_batch22.md and prior logs: Solbergaskolan access restriction, Älta/Stavsborg identity mismatch, Runmarö dormant2026/27 and earlier reconciliation needs. Review logs preserve follow-ups. Do not rerun successful builders/checkpoints/finalizers. Dashboard deferred; on demand only, no unattended schedule.
''')
# Read all current artifact content before replacing it.
report=(B/'REPORT.md').read_text();(B/'REPORT.md').write_text(report.replace('Staged; load/checkpoint pending.','Loaded and checkpointed. Append +11/+8; replay +0/+0. Totals270 evidence/197 codes.22 tests passed; exact staging/target, prior-record preservation, source quotation/hash and official fingerprint checks passed. Ledger233 outcomes/529 pending/762 unique official IDs, not233 resolved schools. Exactly10 rows changed. No reconciled all-county unit-applicability scope counts.'))
status=read(B/'batch_status.json');status.update(status='CHECKPOINTED',documented_outcomes=233,pending=529);dump(B/'batch_status.json',status)
for r in reviews:r['load_state']='Loaded; checkpointed; unresolved follow-ups retained'
with (B/'review_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=reviews[0]);w.writeheader();w.writerows(reviews)
dump(B/'independent_staging_target_check.json',dict(status='PASSED',exact_quotes=11,source_hashes=True,target_tuples=True,official_fingerprints_unchanged=True))
after=list(csv.DictReader(new.open()));assert len(after)==762 and sum(r['review_state']!='Not yet contextually reviewed' for r in after)==233
assert read(P/'next_batch_after_batch22.json')==remaining[:10]
dump(B/'independent_checkpoint_check.json',dict(status='PASSED',official_ids=762,changed_rows=10,unchanged_rows=752,documented_outcomes=233,pending=529,next_selection_matches=True))
print(json.dumps(dict(status='CHECKPOINTED',documented_outcomes=233,pending=529,schools=762)))
