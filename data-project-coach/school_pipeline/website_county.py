"""Resumable county website evidence collection; no confirmed auto-classification."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import socket
import sqlite3
import threading
import time
from urllib.parse import urlsplit, urljoin, urldefrag
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser

import dlt
from prefect import flow
from school_pipeline.flow import ROOT
from school_pipeline.website_focus import Text, candidates

AGENT = 'SchoolCourseProject'
LOCK = threading.Lock()
HOSTS = {}
ROBOTS = {}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def valid_url(url):
    p = urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
        raise ValueError('Unsafe URL')
    if p.port not in (None,80,443): raise ValueError('Nonstandard port')
    for addr in socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80)):
        if not ipaddress.ip_address(addr[4][0]).is_global: raise ValueError('Nonpublic address')
    return p


def host_lock(host):
    with LOCK:
        return HOSTS.setdefault(host, threading.Lock())


def raw(url):
    p = valid_url(url)
    with host_lock(p.hostname):
        time.sleep(0.6)
        try:
            with build_opener(NoRedirect()).open(Request(url,headers={'User-Agent':AGENT+'/0.2 (public school profile research)','Accept':'text/html,text/plain'}),timeout=12) as r:
                data = r.read(1500001)
                if len(data)>1500000: raise ValueError('Response too large')
                return r.status, data.decode(r.headers.get_content_charset() or 'utf-8',errors='replace'),r.headers.get('Content-Type',''),None
        except HTTPError as e:
            if e.code in (301,302,303,307,308):return e.code,'','',urljoin(url,e.headers.get('Location',''))
            return e.code,'','',None


def permission(url,folder):
    p = valid_url(url); origin=f'{p.scheme}://{p.netloc}'
    # Duplicate initial robots requests are harmless; cache values are immutable.
    with LOCK: cached=ROBOTS.get(origin)
    if cached is None:
        robots=origin+'/robots.txt'
        status,body,ctype,redirect=raw(robots)
        for _ in range(4):
            if not redirect: break
            robots=redirect
            status,body,ctype,redirect=raw(robots)
        record={'robots_url':robots,'http_status':status,'checked_at':datetime.now(timezone.utc).isoformat()}
        if status==200 and ('text/plain' in ctype or body.lstrip().startswith(('User-agent','#','user-agent'))):
            rp=RobotFileParser();rp.parse(body.splitlines());record['state']='parsed'
            delay=rp.crawl_delay(AGENT) or rp.crawl_delay('*') or 0
            record['crawl_delay']=delay
        elif status==404:rp=None;record['state']='not_found'
        else:rp=None;record['state']='unresolved'
        cached=(record,rp)
        key=hashlib.sha256(origin.encode()).hexdigest()[:20]
        (folder/'robots').mkdir(exist_ok=True)
        (folder/'robots'/f'{key}.json').write_text(json.dumps({**record,'body':body},ensure_ascii=False))
        with LOCK:ROBOTS[origin]=cached
    record,rp=cached
    if record['state']=='unresolved':raise ValueError('Robots unresolved; manual review required')
    if record.get('crawl_delay',0):raise ValueError('Explicit crawl delay requires manual scheduling')
    if rp and not rp.can_fetch(AGENT,url):raise ValueError('Robots disallowed')
    return record


def page(url,folder):
    trail=[]
    for _ in range(5):
        perm=permission(url,folder);trail.append({'url':url,**perm})
        status,body,ctype,redirect=raw(url)
        if redirect:
            url=redirect;continue
        if status!=200:raise ValueError(f'HTTP {status}')
        if 'html' not in ctype:raise ValueError('Not HTML')
        return url,body,trail
    raise ValueError('Too many redirects')


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href'):self.links.append(d['href'])


def relevant_links(url,html):
    p=Links();p.feed(html);origin=urlsplit(url);result=[];terms=[]
    prefix=origin.path.rstrip('/')
    for href in p.links:
        u=urldefrag(urljoin(url,href))[0];s=urlsplit(u)
        if s.netloc!=origin.netloc or s.query:continue
        if any(w in s.path.lower() for w in ('villkor','terms-of','anvandarvillkor')):terms.append(u)
        # Deep municipal listings must not spill into unrelated units.
        if prefix and not s.path.startswith(prefix+'/'):continue
        if any(w in s.path.lower() for w in ('pedagog','profil','om-skolan','om-oss','grundskola','inriktning','waldorf','montessori')) and u!=url:
            if u not in result:result.append(u)
    return result[:2], sorted(set(terms))


def collect(school,folder):
    code,name,url=school
    base={'school_unit_code':code,'school_name':name,'registered_url':url,'attempted_at':datetime.now(timezone.utc).isoformat(),'review_status':'needs_review','method_version':'county_web_v1'}
    pages=[];evidence=[];errors=[]
    if not url:return {**base,'collection_status':'missing_registered_website','pages':[],'evidence':[]}
    try:
        final,html,trail=page(url,folder)
        links,terms=relevant_links(final,html)
        base['terms_review_status']='terms_link_detected_bulk_followup_paused' if terms else 'no_terms_link_detected_not_legal_clearance'
        base['terms_urls']=terms
        targets=[(final,html,trail)]
        if not terms:
            for link in links:
                try:targets.append(page(link,folder))
                except Exception as e:errors.append({'url':link,'error':str(e)[:250]})
        for i,(source,body,trail) in enumerate(targets):
            parser=Text();parser.feed(body);text=parser.text()
            (folder/f'{code}_{i}.txt').write_text(text,encoding='utf-8')
            pages.append({'source_url':source,'retrieved_at':datetime.now(timezone.utc).isoformat(),'robots_checks':trail,'text_file':f'{code}_{i}.txt'})
            for row in candidates(text):
                excerpt=row['supporting_excerpt']
                if len(excerpt)<65:continue
                eid=hashlib.sha256((code+source+row['category']+excerpt).encode()).hexdigest()
                evidence.append({**row,'evidence_id':eid,'school_unit_code':code,'school_name':name,'source_url':source,'retrieved_at':pages[-1]['retrieved_at'],'scope_status':'school_unit_scope_needs_review'})
        status='fetched_candidates_need_review' if evidence else 'fetched_no_candidate_needs_review'
    except Exception as e:
        status='collection_failed_needs_review';errors.append({'url':url,'error':str(e)[:250]})
    return {**base,'collection_status':status,'pages':pages,'evidence':evidence,'errors':errors}


def save(path,data):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)


@flow(name='county-school-website-evidence',persist_result=False,log_prints=True)
def run(folder_name='outputs/website_county',limit=None):
    raise RuntimeError('Deprecated focus collector disabled; use contextual approach review and DuckDB batch loading.')
    folder=ROOT/folder_name;folder.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(ROOT/'.state/schools.sqlite') as c:
        schools=c.execute('select school_unit_code,name,website from schools order by school_unit_code').fetchall()
    todo=[s for s in schools if not (folder/f'{s[0]}.json').exists()]
    if limit:todo=todo[:limit]
    with ThreadPoolExecutor(max_workers=8) as pool:
        jobs={pool.submit(collect,s,folder):s for s in todo}
        for n,f in enumerate(as_completed(jobs),1):
            result=f.result();save(folder/f"{result['school_unit_code']}.json",result)
            if n%25==0:print('Checkpointed',n,'of',len(todo))
    coverage=[];evidence=[]
    for code,name,url in schools:
        path=folder/f'{code}.json'
        if path.exists():
            row=json.loads(path.read_text());evidence.extend(row.pop('evidence'));coverage.append(row)
        else:coverage.append({'school_unit_code':code,'school_name':name,'registered_url':url,'collection_status':'not_reviewed'})
    evidence=list({row['evidence_id']:row for row in evidence}.values())
    save(folder/'coverage.json',coverage);save(folder/'evidence.json',evidence)
    resources=[dlt.resource(coverage,name='school_focus_county_coverage',write_disposition='merge',primary_key='school_unit_code')]
    if evidence:resources.append(dlt.resource(evidence,name='school_focus_county_candidates',write_disposition='merge',primary_key='evidence_id'))
    pipeline=dlt.pipeline(pipeline_name='county_website_evidence',destination=dlt.destinations.sqlalchemy(f"sqlite:///{ROOT/'.state/schools.sqlite'}"),dataset_name='main',pipelines_dir=str(ROOT/'.state/dlt_county_web'))
    info=pipeline.run(resources);info.raise_on_failed_jobs()
    from collections import Counter
    summary={'statuses':dict(Counter(r['collection_status'] for r in coverage)),'candidate_records':len(evidence),'schools':len(coverage)}
    save(folder/'summary.json',summary);print(summary)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);args=p.parse_args();run(limit=args.limit)
