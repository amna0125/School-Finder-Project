import sys,json
from pathlib import Path
sys.path.insert(0,'..')
import fetch
HERE=Path(__file__).parent;fetch.SRC=HERE/'sources';fetch.SRC.mkdir(exist_ok=True)
from concurrent.futures import ThreadPoolExecutor
U=json.load(open(HERE/'urls.json'));T={t['school_id']:t for t in json.load(open(HERE/'targets.json'))}
def work(sid):
    row=dict(school_id=sid,official_directory_name=T[sid]['name'],registered_url=U[sid])
    try:r=fetch.collect(row)
    except Exception as e:r=dict(school_id=sid,name=T[sid]['name'],registered_url=U[sid],pages=[],events=[dict(error=repr(e)[:300])],outcome_hint='error')
    r['original_registered_url']=T[sid]['reg'];r['followup_url']=U[sid];return r
with ThreadPoolExecutor(10) as ex, open(HERE/'collection.jsonl','w') as f:
    for r in ex.map(work,list(U)):
        f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();print(r['school_id'],r['name'][:25],r['outcome_hint'],len(r['pages']),flush=True)
