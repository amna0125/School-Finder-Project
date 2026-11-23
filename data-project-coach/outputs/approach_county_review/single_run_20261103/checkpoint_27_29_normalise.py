"""Checkpoint Batches27-29 after load, and normalise review_state labels."""
import csv,json,sys,collections,difflib
from pathlib import Path
import duckdb
sys.path.insert(0,str(Path(__file__).parent))
from labels import *
P=Path('outputs/approach_county_review')
old=P/'county_progress_20261102_after_batch26.csv'; new=P/'county_progress_20261103_after_batch29_normalised.csv'
assert not new.exists()
rows=list(csv.DictReader(old.open()))
db=duckdb.connect('.state/schools.duckdb',read_only=True)
codes=collections.Counter(r[0] for r in db.execute('select school_id from approach_codes').fetchall())
assert db.execute('select count(*) from approach_evidence').fetchone()[0]==325 and db.execute('select count(*) from approach_codes').fetchone()[0]==233
# batch 27-29 outcomes
upd={}
for b in ['batch27_10schools_20261102','batch28_10schools_20261102','batch29_10schools_20261102']:
    for r in csv.DictReader((P/b/'review_log.csv').open()):
        note=r.get('unit_scope') or r.get('note') or r.get('decision') or ''
        fu=r.get('follow_up') or r.get('unresolved_follow_up') or ''
        upd[r['school_id']]=dict(review_state=r['outcome'],batch_reference=b,note=(note+(' Follow-up: '+fu if fu and fu!=note else '')).strip())
assert len(upd)==30
out=[]
for r in rows:
    r=dict(r)
    if r['school_id'] in upd:
        assert r['review_state']=='Not yet contextually reviewed'
        u=upd[r['school_id']];r['batch_reference']=u['batch_reference'];r['note']=u['note']
        r['review_state']=u['review_state']
        r['collection_status']={'Permission blocker':'terms_review_required'}.get(u['review_state'],'contextually_reviewed_followups_retained')
    lab,reason=normalise(r['school_id'],r['review_state'],codes[r['school_id']]>0)
    if lab==REVIEWED: assert codes[r['school_id']]>0,(r['school_id'],r['review_state'])
    elif lab!=PENDING: assert codes[r['school_id']]==0,(r['school_id'],r['review_state'])
    out.append(dict(school_id=r['school_id'],official_directory_name=r['official_directory_name'],review_state=lab,flag_for_joint_review='yes' if lab in FLAGGED else '',flag_reason=reason,review_state_original_wording=r['review_state'],batch_reference=r['batch_reference'],collection_status=r['collection_status'],registered_url=r['registered_url'],note=r['note']))
assert len(out)==762
with new.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
c=collections.Counter(r['review_state'] for r in out)
mapping=collections.Counter((r['review_state_original_wording'],r['review_state']) for r in out)
(P/'single_run_20261103'/'label_mapping.json').write_text(json.dumps([dict(original=k[0],standard=k[1],schools=v) for k,v in sorted(mapping.items())],ensure_ascii=False,indent=2))
for b in upd.values(): pass
for b in ['batch27_10schools_20261102','batch28_10schools_20261102','batch29_10schools_20261102']:
    s=json.loads((P/b/'batch_status.json').read_text());s.update(status='LOADED_CHECKPOINTED',database_loaded=True,county_checkpointed=True,checkpoint_ledger=new.name);(P/b/'batch_status.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(c,indent=1))
