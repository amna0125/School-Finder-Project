import sys,json,re,hashlib,time,urllib.parse
from pathlib import Path
sys.path.insert(0,'..')
import fetch
HERE=Path(__file__).parent;fetch.SRC=HERE/'sources'
from fetch import get,parse_html,KEY,SKIP,fold,name_tokens
from concurrent.futures import ThreadPoolExecutor
rows=[json.loads(l) for l in open(HERE/'collection.jsonl')]
def ext(c):
    if c['outcome_hint']!='collected' or len(c['pages'])>=3:return c
    p0=c['pages'][-1];html=(HERE/p0['source_file']).read_bytes();_,_,links=parse_html(html)
    base=p0['source_url'];bp=urllib.parse.urlparse(base)
    slug=re.sub(r'(\.4\.[0-9a-f]+)?\.html$','',bp.path.rstrip('/')).rsplit('/',1)[-1]
    seen={p['source_url'].rstrip('/') for p in c['pages']};cand=[]
    for h,t in links:
        u=urllib.parse.urljoin(base,h).split('#')[0];p=urllib.parse.urlparse(u)
        if p.netloc!=bp.netloc or slug not in p.path or SKIP.search(p.path) or u.rstrip('/') in seen:continue
        s=bool(KEY.search(p.path))*2+bool(KEY.search(t))
        if s:cand.append((-s,len(u),u))
    for _,_,u in sorted(set(cand))[:6]:
        if len(c['pages'])>=4:break
        r=get(u)
        if r.get('http_status')==200 and 'html' in r.get('ctype','') and r['final_url'].rstrip('/') not in seen:
            seen.add(r['final_url'].rstrip('/'))
            title,text,_=parse_html(r['content']);fn=f"{c['school_id']}_{len(c['pages'])}"
            (fetch.SRC/(fn+'.html')).write_bytes(r['content']);(fetch.SRC/(fn+'.txt')).write_text(text)
            c['pages'].append(dict(label='linked_followup',requested_url=u,source_url=r['final_url'],http_status=200,page_title=title,source_file='sources/'+fn+'.html',text_file='sources/'+fn+'.txt',sha256=hashlib.sha256(r['content']).hexdigest(),accessed_date=time.strftime('%Y-%m-%d',time.gmtime())))
    return c
with ThreadPoolExecutor(10) as ex:out=list(ex.map(ext,rows))
open(HERE/'collection.jsonl','w').write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in out))
import collections;print(collections.Counter(len(r['pages']) for r in out))
