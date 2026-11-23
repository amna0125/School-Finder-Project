"""Manual check by Amna (2026-11-09): last 5 flagged schools, from the editable table in the Claude Doc 'Manual check guide: approach codes'."""
import csv,json,sys,duckdb,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;SR=HERE.parent;P=SR.parent
sys.path.insert(0,str(SR))
from labels import *
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE='2026-11-09';TAG=f'Manual check by Amna ({DATE})'
db='/home/user/proj/.state/schools.duckdb'
dec=json.loads((HERE/'decisions.json').read_text())
E=[];C=[];LV={'E':('Explicit','High'),'S':('Supported','Medium')}
for d in dec:
    nc=0
    for k,ev in enumerate(d['ev']):
        eid=f"ae_man_{d['sid']}_{k+1:02d}"
        E.append(dict(evidence_id=eid,school_id=d['sid'],source_url=d['url'],page_title=d['title'],accessed_date=DATE,quoted_text=ev['q'],evidence_type='Manual check by Amna; school webpage',interpretation_note=TAG+': '+ev['i']))
        for cat,sub,lv in ev['c']:
            nc+=1;C.append(dict(code_id=f"ac_man_{d['sid']}_{nc:02d}",school_id=d['sid'],category=cat,subcategory=sub,coding_level=LV[lv][0],confidence=LV[lv][1],evidence_id=eid,coder_note=TAG+'; coded by Amna from the public page, loaded by the assistant. Website claim, not independently verified practice.'+(' Unit identity confirmed: '+d['identity'] if d.get('identity') else ''),review_status='Reviewed'))
validate_records(E,C)
CH=HERE/'load';CH.mkdir(exist_ok=True)
(CH/'Approach_evidence.staged.json').write_text(json.dumps(E,ensure_ascii=False,indent=2)+'\n')
(CH/'Approach_codes.staged.json').write_text(json.dumps(C,ensure_ascii=False,indent=2)+'\n')
if not (CH/'load_validation.json').exists():
    rep=append_batch(str(CH),db);assert rep['status']=='PASSED',rep
O={'R':REVIEWED,'P':NOPAGE,'N':NOCLEAR}
rows=list(csv.DictReader(open(P/'county_progress_20261103_after_step4.csv')));by={r['school_id']:r for r in rows}
for d in dec:
    x=by[d['sid']];assert x['review_state'] in FLAGGED,(d['sid'],x['review_state'])
    st=O[d['o']];note=d.get('note') or '; '.join(ev['i'] for ev in d['ev'])
    x.update(review_state=st,flag_for_joint_review='no',flag_reason='',batch_reference='single_run_20261103/manual',note=TAG+': '+note+' | Earlier: '+x['note'][:300])
out=P/'county_progress_20261103_after_manual.csv'
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
con=duckdb.connect(db,read_only=True)
codes=collections.Counter(x[0] for x in con.execute('select school_id from approach_codes').fetchall())
for x in rows:
    if x['review_state']==REVIEWED:assert codes[x['school_id']]>0,x['school_id']
    else:assert codes[x['school_id']]==0,x['school_id']
fl=[x for x in rows if x['review_state'] in FLAGGED]
print(json.dumps(dict(evidence=len(E),codes=len(C),county=collections.Counter(x['review_state'] for x in rows),flagged=len(fl),db=con.execute('select count(*) from approach_evidence').fetchone()[0],dbc=con.execute('select count(*) from approach_codes').fetchone()[0]),ensure_ascii=False))
