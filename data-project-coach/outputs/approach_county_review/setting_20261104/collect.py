import sys,json,csv,duckdb
from pathlib import Path
HERE=Path(__file__).resolve().parent;SR=HERE.parent/'single_run_20261103'
sys.path.insert(0,str(SR))
import fetch
fetch.SRC=HERE/'sources';fetch.SRC.mkdir(exist_ok=True)
from concurrent.futures import ThreadPoolExecutor
have=set()
for f in [SR/'collection.jsonl',SR/'followup/collection.jsonl']:
    for l in open(f):
        d=json.loads(l)
        if any(p.get('http_status')==200 and p.get('text_file') for p in d['pages']): have.add(d['school_id'])
led=list(csv.DictReader(open(HERE.parent/'county_progress_20261103_after_step3b.csv')))
c=duckdb.connect('/home/user/proj/.state/schools.duckdb',read_only=True)
ev={}
for s,u in c.execute('select school_id,source_url from approach_evidence order by evidence_id').fetchall(): ev.setdefault(s,[]).append(u)
todo=[r for r in led if r['school_id'] not in have and not r['review_state'].startswith('Blocked')]
def work(r):
    url=(ev.get(r['school_id']) or [r['registered_url']])[0]
    row=dict(school_id=r['school_id'],official_directory_name=r['official_directory_name'],registered_url=url)
    try:x=fetch.collect(row)
    except Exception as e:x=dict(school_id=r['school_id'],name=r['official_directory_name'],registered_url=url,pages=[],events=[dict(error=repr(e)[:300])],outcome_hint='error')
    return x
print(len(todo),flush=True)
with ThreadPoolExecutor(8) as ex, open(HERE/'collection.jsonl','w') as f:
    for x in ex.map(work,todo):
        f.write(json.dumps(x,ensure_ascii=False)+'\n');f.flush();print(x['school_id'],x.get('outcome_hint'),len(x['pages']),flush=True)
