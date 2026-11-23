import sys,json,hashlib,time
from pathlib import Path
sys.path.insert(0,'..')
import fetch
HERE=Path(__file__).parent;fetch.SRC=HERE/'sources'
from fetch import get,parse_html,render
rows={json.loads(l)['school_id']:json.loads(l) for l in open(HERE/'collection.jsonl')}
def add(sid,url,force_render=False,replace_idx=None):
    c=rows[sid];r=get(url)
    if r.get('http_status')!=200:print(sid,url,'FAIL',{k:v for k,v in r.items() if k!='content'});return
    title,text,_=parse_html(r['content'])
    if force_render or len(text)<200:
        r=render(r);title,text,_=parse_html(r['content'])
    i=replace_idx if replace_idx is not None else len(c['pages'])
    fn=f"{sid}_{i}";(fetch.SRC/(fn+'.html')).write_bytes(r['content']);(fetch.SRC/(fn+'.txt')).write_text(text)
    pg=dict(label='followup_added'+('+rendered' if r.get('rendered') else ''),requested_url=url,source_url=r['final_url'],http_status=200,page_title=title,source_file='sources/'+fn+'.html',text_file='sources/'+fn+'.txt',sha256=hashlib.sha256(r['content']).hexdigest(),accessed_date=time.strftime('%Y-%m-%d',time.gmtime()))
    if replace_idx is not None:c['pages'][i]=pg
    else:c['pages'].append(pg)
    c['outcome_hint']='collected';print(sid,i,title,len(text))
for a in json.loads(sys.argv[1]):add(*a)
open(HERE/'collection.jsonl','w').write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows.values()))
