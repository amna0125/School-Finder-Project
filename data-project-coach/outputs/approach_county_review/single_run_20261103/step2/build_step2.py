"""Joint review step 2 (2026-11-03): apply agreed rules A (provider-wide claims to chain units, Supported, Provider webpage),
C (accept website when name/address match; else unit identity), D (move to step 3). Group B untouched pending Amna."""
import csv,json,re,sys,duckdb
from pathlib import Path
HERE=Path(__file__).parent;SR=HERE.parent;P=SR.parent
sys.path.insert(0,str(SR))
from labels import *
from fetch import parse_html
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
def ws(x):return re.sub(r'\s+',' ',x.replace('­','')).strip()
pages={}
for f in [SR/'collection.jsonl',SR/'followup/collection.jsonl']:
    base=f.parent
    for l in open(f):
        d=json.loads(l)
        for p in d['pages']:pages.setdefault(p['source_url'],(base,p))
db=SR.parent.parent.parent/'.state'/'schools.duckdb'
con=duckdb.connect(str(db),read_only=True)
dec=json.loads((HERE/'decisions.json').read_text())
E=[];C=[];R=[]
LV={'E':('Explicit','High'),'S':('Supported','Medium')}
for d in dec:
    sid=d['sid'];nc=0
    for k,ev in enumerate(d.get('ev',[])):
        if 'url' in ev:
            base,p=pages[ev['url']]
            text=ws(parse_html((base/p['source_file']).read_bytes())[1]);q=ws(ev['q']);assert q in text,(sid,q[:60])
            meta=dict(source_url=p['source_url'],page_title=ws(p['page_title']) if p['page_title'] else None,accessed_date=p['accessed_date'])
        else:  # reuse an already-validated evidence row (group C)
            row=con.execute('select source_url,page_title,accessed_date,quoted_text from approach_evidence where school_id=? and quoted_text=?',[sid,ev['q']]).fetchone()
            assert row,(sid,ev['q'][:60]);q=row[3];meta=dict(source_url=row[0],page_title=row[1],accessed_date=row[2])
        eid=f'ae_s2_{sid}_{k+1:02d}'
        E.append(dict(evidence_id=eid,school_id=sid,quoted_text=q,evidence_type=ev.get('t','School webpage'),interpretation_note=ev['i'],**meta))
        for cat,sub,lv in ev['c']:
            nc+=1;C.append(dict(code_id=f'ac_s2_{sid}_{nc:02d}',school_id=sid,category=cat,subcategory=sub,coding_level=LV[lv][0],confidence=LV[lv][1],evidence_id=eid,coder_note='Joint review step 2 (2026-11-03), rule agreed with Amna; assistant application, not independently verified practice. '+ev.get('cn',''),review_status='Reviewed'))
    R.append(d)
validate_records(E,C)
CH=HERE/'load';CH.mkdir(exist_ok=True)
(CH/'Approach_evidence.staged.json').write_text(json.dumps(E,ensure_ascii=False,indent=2)+'\n')
(CH/'Approach_codes.staged.json').write_text(json.dumps(C,ensure_ascii=False,indent=2)+'\n')
con.close()
if not (CH/'load_validation.json').exists():
    rep=append_batch(str(CH),str(db));assert rep['status']=='PASSED'
O={'R':REVIEWED,'U':UNCERTAIN,'N':NOCLEAR,'B':BLOCKED}
led=P/'county_progress_20261103_after_followup_blocked.csv'
rows=list(csv.DictReader(led.open()));by={r['school_id']:r for r in rows}
for d in R:
    x=by[d['sid']];assert x['review_state']==UNCERTAIN,(d['sid'],x['review_state'])
    st=O[d['o']]
    x.update(review_state=st,flag_for_joint_review='yes' if st in FLAGGED else '',flag_reason=d.get('why',''),batch_reference='single_run_20261103/step2',note=d['note']+' | Earlier: '+x['note'][:300])
new=P/'county_progress_20261103_after_step2.csv'
with new.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
con=duckdb.connect(str(db),read_only=True)
import collections
codes=collections.Counter(x[0] for x in con.execute('select school_id from approach_codes').fetchall())
for x in rows:
    if x['review_state']==REVIEWED:assert codes[x['school_id']]>0,x['school_id']
    elif x['review_state']!=PENDING:assert codes[x['school_id']]==0,x['school_id']
print(json.dumps(dict(schools=len(R),evidence=len(E),codes=len(C),county=collections.Counter(x['review_state'] for x in rows),db=dict(evidence=con.execute('select count(*) from approach_evidence').fetchone()[0],codes=con.execute('select count(*) from approach_codes').fetchone()[0])),ensure_ascii=False))
