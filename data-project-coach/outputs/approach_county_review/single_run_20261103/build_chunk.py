"""Stage, load (dlt/Prefect append) and checkpoint one chunk of the single run.
Usage: python build_chunk.py NN   (reads decisions/chunkNN.json)"""
import csv,json,sys,re,hashlib,collections,difflib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from labels import *
from fetch import parse_html
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
import duckdb
ROOT=Path(__file__).parent;P=ROOT.parent
N=int(sys.argv[1]);CH=ROOT/f'chunk{N:02d}';CH.mkdir(exist_ok=True)
dec=json.loads((ROOT/'decisions'/f'chunk{N:02d}.json').read_text())
col={}
for l in (ROOT/'collection.jsonl').open():
    d=json.loads(l);col[d['school_id']]=d
O={'R':REVIEWED,'U':UNCERTAIN,'N':NOCLEAR,'B':BLOCKED}
CATS={'Arts and creative learning','Alternative pedagogy','Project- or inquiry-based learning','Outdoor, nature, or place-based learning','Language, international, or intercultural profile','Support, inclusion, or wellbeing emphasis','Other stated profile'}
LV={'E':('Explicit','High'),'S':('Supported','Medium')}
E=[];C=[];R=[];L=[]
def ws(x):return re.sub(r'\s+',' ',x.replace('\u00ad','')).strip()
for d in dec:
    sid=d['sid'];c=col[sid];o=O[d['o']]
    nc=0
    for k,ev in enumerate(d.get('ev',[])):
        p=c['pages'][ev['p']]
        text=ws(parse_html((ROOT/p['source_file']).read_bytes())[1])
        q=ws(ev['q']);assert q in text,(sid,q[:80])
        eid=f'ae_sr_{sid}_{k+1:02d}'
        E.append(dict(evidence_id=eid,school_id=sid,source_url=p['source_url'],page_title=(ws(p['page_title']) if p['page_title'] else None),accessed_date=p['accessed_date'],quoted_text=q,evidence_type=ev.get('t','School webpage'),interpretation_note=ev['i']))
        for cat,sub,lv in ev.get('c',[]):
            assert cat in CATS,cat
            nc+=1
            C.append(dict(code_id=f'ac_sr_{sid}_{nc:02d}',school_id=sid,category=cat,subcategory=sub,coding_level=LV[lv][0],confidence=LV[lv][1],evidence_id=eid,coder_note='Assistant contextual review (single run 2026-11-03, codebook v1), not human review or independently verified practice. '+ev.get('cn',''),review_status='Reviewed'))
    if o==REVIEWED:assert nc>0,sid
    else:assert nc==0,sid
    R.append(dict(school_id=sid,official_directory_name=c['name'],review_state=o,flag_reason=d.get('why',''),note=d['note'],reviewer='Assistant contextual review; not human or independent practice verification',review_date='2026-11-03',pages_reviewed='; '.join(p['source_url'] for p in c['pages']),evidence=sum(e['school_id']==sid for e in E),codes=nc))
    for p in c['pages']:
        L.append(dict(school_id=sid,registered_url=c['registered_url'],requested_url=p['requested_url'],final_url=p['source_url'],page_title=p['page_title'],accessed_date=p['accessed_date'],http_status=p['http_status'],source_file='../'+p['source_file'],sha256=p['sha256'],collection_outcome=c['outcome_hint'],events=''))
    if not c['pages']:
        L.append(dict(school_id=sid,registered_url=c['registered_url'],requested_url='',final_url='',page_title='',accessed_date='2026-11-03',http_status='',source_file='',sha256='',collection_outcome=c['outcome_hint'],events=json.dumps(c['events'],ensure_ascii=False)[:500]))
validate_records(E,C)
assert len({r['school_id'] for r in R})==len(R)
def w(name,rows):
    with (CH/name).open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
(CH/'Approach_evidence.staged.json').write_text(json.dumps(E,ensure_ascii=False,indent=2)+'\n')
(CH/'Approach_codes.staged.json').write_text(json.dumps(C,ensure_ascii=False,indent=2)+'\n')
w('review_log.csv',R);w('collection_log.csv',L)
# load
db_path=P.parent.parent/'.state'/'schools.duckdb'
if E and C and not (CH/'load_validation.json').exists():
    rep=append_batch(str(CH),str(db_path))
    assert rep['status']=='PASSED'
# checkpoint ledger
led=sorted(P.glob('county_progress_20261103_*.csv'),key=lambda p:p.stat().st_mtime)[-1]
rows=list(csv.DictReader(led.open()));by={r['school_id']:r for r in rows}
for r in R:
    x=by[r['school_id']]
    if x['review_state']!=PENDING:assert x['batch_reference']==CH.name,(r['school_id'],x['review_state'])
    x.update(review_state=r['review_state'],flag_for_joint_review='yes' if r['review_state'] in FLAGGED else '',flag_reason=r['flag_reason'],review_state_original_wording='',batch_reference='single_run_20261103/'+CH.name,collection_status=col[r['school_id']]['outcome_hint'],note=r['note'])
new=P/f'county_progress_20261103_after_chunk{N:02d}.csv'
with new.open('w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
con=duckdb.connect(str(db_path),read_only=True)
codes=collections.Counter(x[0] for x in con.execute('select school_id from approach_codes').fetchall())
for x in rows:
    if x['review_state']==REVIEWED:assert codes[x['school_id']]>0,x['school_id']
    elif x['review_state']!=PENDING:assert codes[x['school_id']]==0,x['school_id']
tot=dict(evidence=con.execute('select count(*) from approach_evidence').fetchone()[0],codes=con.execute('select count(*) from approach_codes').fetchone()[0])
st=dict(chunk=N,schools=len(R),evidence=len(E),codes=len(C),outcomes=collections.Counter(r['review_state'] for r in R),ledger=new.name,county=collections.Counter(x['review_state'] for x in rows),db_totals=tot,loaded=(CH/'load_validation.json').exists())
(CH/'chunk_status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2))
print(json.dumps(st,ensure_ascii=False))
