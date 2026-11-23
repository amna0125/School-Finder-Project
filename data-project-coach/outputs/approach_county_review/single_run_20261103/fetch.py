"""Collect school-specific public pages for pending schools (single run 2026-11-03).
Public pages only; robots.txt respected (generic and Claude/AI user-agents); no login/bypass."""
import csv,json,re,sys,time,hashlib,threading,urllib.parse,urllib.robotparser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).parent; SRC=ROOT/'sources'; SRC.mkdir(exist_ok=True)
UA='Mozilla/5.0 (compatible; Claude-User; school-approach-research; +https://claude.ai)'
AI_AGENTS=['ClaudeBot','Claude-User','anthropic-ai','Claude-Web']
KEY=re.compile(r'om-?skolan|om-?oss|var-?skola|pedagogik|profil|inriktning|arbetss[aä]tt|sa-?har-?arbetar|sa-?arbetar|sa-?jobbar|jobbar-?vi|var-?verksamhet|undervisning|vart-?arbetssatt|about|our-?school|vision|v[aä]rdegrund|koncept|idé|ide$|metod|larande|lärande|grundskola',re.I)
SKIP=re.compile(r'aktuellt|nyheter|skolrestaurang|terminstider|skollov|lovdagar|fritid|rektor|matsedel|skolmat|sjukanm|login|logga|jobb|lediga|kontakt|press|nyhet|news|kalender|matsedel|meny|lunch|ansok|ansök|kö|\.pdf$|\.jpg$|\.png$|facebook|instagram|linkedin|youtube|mailto:|tel:|cookie|integritet|gdpr|personuppgift|tillganglighet|sitemap|rss|#',re.I)
host_locks={};robots_cache={};glock=threading.Lock()
def norm(u):
    u=u.strip()
    if not u:return ''
    if not re.match(r'https?://',u):u='http://'+u
    return u
def lock(h):
    with glock:return host_locks.setdefault(h,[threading.Lock(),0.0])
def robots(url):
    p=urllib.parse.urlparse(url);base=f'{p.scheme}://{p.netloc}'
    with glock:
        if base in robots_cache:return robots_cache[base]
    rp=urllib.robotparser.RobotFileParser();info=dict(robots_url=base+'/robots.txt')
    try:
        r=requests.get(base+'/robots.txt',headers={'User-Agent':UA},timeout=20)
        info['http_status']=r.status_code
        if r.status_code==200 and 'html' not in r.headers.get('content-type',''):
            rp.parse(r.text.splitlines());info['state']='parsed';info['sha256']=hashlib.sha256(r.content).hexdigest()
            fn=SRC/('robots_'+re.sub(r'[^a-z0-9]+','_',p.netloc.lower())+'.txt');fn.write_bytes(r.content)
        else: rp=None;info['state']='no_robots_policy'
    except Exception as e: rp=None;info['state']='robots_error';info['error']=str(e)[:200]
    res=(rp,info)
    with glock:robots_cache[base]=res
    return res
def allowed(url):
    rp,info=robots(url)
    if rp is None:return True,'no robots policy',0
    for a in AI_AGENTS+['*']:
        if not rp.can_fetch(a,url):return False,f'robots disallows {a}',0
    d=rp.crawl_delay('*') or 0
    return True,'robots allows',min(float(d),10)
def get(url):
    ok,why,delay=allowed(url)
    if not ok:return dict(requested_url=url,blocked=why)
    h=urllib.parse.urlparse(url).netloc;l=lock(h)
    with l[0]:
        w=max(1.0,delay)-(time.time()-l[1])
        if w>0:time.sleep(w)
        try:
            r=requests.get(url,headers={'User-Agent':UA,'Accept-Language':'sv,en','Accept-Encoding':'gzip, deflate'},timeout=30,allow_redirects=True)
            res=dict(requested_url=url,final_url=r.url,http_status=r.status_code,ctype=r.headers.get('content-type',''),content=r.content)
        except Exception as e:res=dict(requested_url=url,error=str(e)[:200])
        l[1]=time.time()
    if 'final_url' in res and res['final_url']!=url:
        ok,why,_=allowed(res['final_url'])
        if not ok:return dict(requested_url=url,blocked=why+' (after redirect)')
    return res
_pw_lock=threading.Lock()
def render(r):
    try:
        from playwright.sync_api import sync_playwright
        with _pw_lock, sync_playwright() as pw:
            b=pw.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--no-sandbox']);pg=b.new_page(user_agent=UA);pg.goto(r['final_url'],timeout=40000,wait_until='networkidle')
            html=pg.content().encode();b.close()
        return dict(r,content=html,rendered=True)
    except Exception as e:return r
def parse_html(content):
    s=BeautifulSoup(content,'lxml')
    title=(s.title.get_text(' ',strip=True) if s.title else None)
    links=[(a.get('href'),a.get_text(' ',strip=True)) for a in s.find_all('a',href=True)]
    for t in s(['script','style','noscript','svg','header','footer','nav','form','iframe']):t.decompose()
    main=s.find('main')
    if main is None or len(main.get_text(' ',strip=True))<200: main=s.body or s
    text='\n'.join(x.strip() for x in main.get_text('\n').split('\n') if x.strip())
    return title,text,links
def fold(x):
    x=x.lower()
    for a,b in [('å','a'),('ä','a'),('ö','o'),('é','e'),('ü','u')]:x=x.replace(a,b)
    return re.sub(r'[^a-z0-9]+',' ',x).strip()
def name_tokens(name):
    stop={'skola','skolan','grundskola','grundskolan','f','9','6','3','ab','i','och','the','school','ak','arskurs','enhet'}
    return [t for t in fold(name).split() if t not in stop and len(t)>2]
GENERIC_HOSTS={'www.solna.se','solna.se','www.huddinge.se','www.norrtalje.se','www.jarfalla.se','www.sodertalje.se','haninge.se','www.haninge.se','www.taby.se','www.botkyrka.se','www.osteraker.se','www.tyreso.se','www.lidingo.se','lidingo.se','www.sollentuna.se','www.upplands-bro.se','www.sigtuna.se','www.danderyd.se','www.varmdo.se','varmdo.se','www.sundbyberg.se','www.ekero.se','www.upplandsvasby.se','www.vallentuna.se','nynashamn.se','www.nykvarn.se','salem.se','www.nacka.se','www.vaxholm.se'}
LIST=re.compile(r'grundskol|skolor|hitta|skola|utbildning|barn',re.I)
page_cache={}
def cached(u):
    with glock:
        if u in page_cache:return page_cache[u]
    r=get(u);res=None
    if r.get('http_status')==200 and 'html' in r.get('ctype',''):
        t,x,l=parse_html(r['content']);res=(r['final_url'],t,l)
    with glock:page_cache[u]=res
    return res
def find_school(start,links,tokens,host,maxfetch=12):
    def match(links,base):
        best=[]
        for href,txt in links:
            u=urllib.parse.urljoin(base,href).split('#')[0];p=urllib.parse.urlparse(u)
            if p.scheme not in('http','https') or SKIP.search(p.path):continue
            f=fold(txt+' '+p.netloc+' '+p.path)
            if all(t in f for t in tokens) and ('skol' in f or 'skola' in fold(txt) or p.netloc!=host):best.append((len(u),u))
        return sorted(best)[0][1] if best else None
    m=match(links,start)
    if m:return m
    queue=[];seen={start}
    def add(links,base):
        for href,txt in links:
            u=urllib.parse.urljoin(base,href).split('#')[0];p=urllib.parse.urlparse(u)
            if p.netloc==host and u not in seen and LIST.search(p.path) and not SKIP.search(p.path) and p.path.count('/')<=5:
                seen.add(u);queue.append((-(('grundskol' in u)+('hitta' in u)+('skolor' in u)),len(u),u))
    add(links,start);n=0
    while queue and n<maxfetch:
        queue.sort();_,_,u=queue.pop(0);n+=1
        res=cached(u)
        if not res:continue
        fu,t,l=res;m=match(l,fu)
        if m:return m
        add(l,fu)
    return None
def collect(row,maxpages=5):
    sid=row['school_id'];name=row['official_directory_name'];reg=norm(row['registered_url'])
    out=dict(school_id=sid,name=name,registered_url=row['registered_url'],pages=[],events=[])
    if not reg:out['outcome_hint']='no_registered_website';return out
    r=get(reg)
    if 'blocked' in r:out['events'].append(r);out['outcome_hint']='permission_blocked';return out
    if r.get('http_status')!=200 or 'html' not in r.get('ctype',''):
        if reg.startswith('http://'):
            r2=get('https://'+reg[7:])
            if r2.get('http_status')==200:r=r2
        if r.get('http_status')!=200:out['events'].append({k:v for k,v in r.items() if k!='content'});out['outcome_hint']='inaccessible';return out
    tokens=name_tokens(name)
    def save(r,label):
        title,text,links=parse_html(r['content'])
        if len(text)<200: r=render(r);title,text,links=parse_html(r['content']);label+=('+rendered' if r.get('rendered') else '')
        fn=f'{sid}_{len(out["pages"])}'
        (SRC/(fn+'.html')).write_bytes(r['content']);(SRC/(fn+'.txt')).write_text(text)
        out['pages'].append(dict(label=label,requested_url=r['requested_url'],source_url=r['final_url'],http_status=r['http_status'],page_title=title,source_file='sources/'+fn+'.html',text_file='sources/'+fn+'.txt',sha256=hashlib.sha256(r['content']).hexdigest(),accessed_date=time.strftime('%Y-%m-%d',time.gmtime())))
        return title,text,links
    title,text,links=save(r,'registered')
    start=r['final_url'];sp=urllib.parse.urlparse(start)
    # generic municipal landing page -> follow school-listing links (same host) to a page naming the school
    generic=(sp.netloc in GENERIC_HOSTS and (len(sp.path.strip('/'))<2 or not (tokens and all(t in fold(sp.path)+' '+fold(title or '') for t in tokens[:1]))))
    if generic and tokens:
        found=find_school(start,links,tokens,sp.netloc)
        if found:
            r2=get(found)
            if r2.get('http_status')==200 and 'html' in r2.get('ctype',''):
                title,text,links=save(r2,'school_page_from_registered_listing');start=r2['final_url'];sp=urllib.parse.urlparse(start);generic=False
        if generic:
            out['outcome_hint']='school_page_not_found';out['events'].append(dict(note='registered URL is a general municipal page; no page naming the school found within its school listings'));return out
    prefix='/' if sp.path in ('','/') else sp.path.rstrip('/')+'/'
    if not generic and sp.netloc not in GENERIC_HOSTS and sp.path.count('/')<=1: prefix='/'
    seen={p['source_url'].rstrip('/') for p in out['pages']}
    cand=[]
    for href,txt in links:
        u=urllib.parse.urljoin(start,href).split('#')[0]
        p=urllib.parse.urlparse(u)
        if p.netloc!=sp.netloc or not (p.path.rstrip('/')+'/').startswith(prefix) or SKIP.search(p.path) or u.rstrip('/') in seen:continue
        s=bool(KEY.search(p.path))*2+bool(KEY.search(txt))
        if s:cand.append((-s,len(u),u))
    for _,_,u in sorted(set(cand))[:maxpages*2]:
        if len(out['pages'])>=maxpages:break
        if u.rstrip('/') in seen:continue
        seen.add(u.rstrip('/'))
        r3=get(u)
        if r3.get('http_status')==200 and 'html' in r3.get('ctype','') and r3['final_url'].rstrip('/') not in {p['source_url'].rstrip('/') for p in out['pages']}:
            save(r3,'linked')
        elif 'blocked' in r3:out['events'].append(r3)
    out['outcome_hint']='collected'
    return out
if __name__=='__main__':
    rows=[x for x in csv.DictReader(open(sys.argv[1])) if x['review_state']=='Not yet reviewed']
    ids=set(sys.argv[2].split(',')) if len(sys.argv)>2 else None
    if ids:rows=[r for r in rows if r['school_id'] in ids]
    done=set()
    resf=ROOT/'collection.jsonl'
    if resf.exists():done={json.loads(l)['school_id'] for l in resf.open()}
    rows=[r for r in rows if r['school_id'] not in done]
    def work(r):
        if r['collection_status']=='terms_review_required':return dict(school_id=r['school_id'],name=r['official_directory_name'],registered_url=r['registered_url'],pages=[],events=[dict(note='terms_review_required retained from earlier collection; not fetched')],outcome_hint='terms_review_required')
        try:return collect(r)
        except Exception as e:return dict(school_id=r['school_id'],name=r['official_directory_name'],registered_url=r['registered_url'],pages=[],events=[dict(error=repr(e)[:300])],outcome_hint='error')
    with ThreadPoolExecutor(12) as ex, resf.open('a') as f:
        for i,res in enumerate(ex.map(work,rows)):
            f.write(json.dumps(res,ensure_ascii=False)+'\n');f.flush()
            print(i,res['school_id'],res['outcome_hint'],len(res['pages']),flush=True)
