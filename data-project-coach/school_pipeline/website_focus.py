"""Conservative website evidence pilot; suggestions are never confirmed labels."""
import json
import re
import sqlite3
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser

from school_pipeline.flow import ROOT
import dlt
from prefect import flow, task

AGENT = 'SchoolCourseProject'
TAXONOMY = {
    'academic_subject_specialist': 'Explicit academic/subject-specialist profile',
    'creative_arts': 'Creative, visual or performing arts',
    'music': 'Music', 'montessori': 'Montessori', 'waldorf': 'Waldorf',
    'other_named_pedagogy': 'Other explicitly named pedagogy',
    'sport': 'Sport/physical activity', 'language_international': 'Language/international',
    'other_explicit_focus': 'Other explicit focus'}
# Candidate extraction only. Generic academic claims do not qualify.
PATTERNS = {
    'academic_subject_specialist': r'\b(?:matematikprofil|science profile|naturvetenskaplig profil)\b',
    'creative_arts': r'\b(?:konst|konstnärlig\w*|estetisk\w*|teater|dans|drama)\b',
    'music': r'\b(?:musik\w*|music)\b',
    'montessori': r'\bmontessori\w*\b', 'waldorf': r'\bwaldorf\w*\b',
    'other_named_pedagogy': r'\b(?:Reggio Emilia|Freinet)\b',
    'sport': r'\b(?:idrottsprofil|fotbollsprofil|sports profile)\b',
    'language_international': r'\b(?:språkprofil|tvåspråkig\w*|bilingual|international curriculum)\b'}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'footer', 'header'): self.skip += 1
        if tag in ('p','div','h1','h2','h3','li','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'footer', 'header'): self.skip = max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)
    def text(self):
        return '\n'.join(' '.join(line.split()) for line in ''.join(self.parts).splitlines() if line.strip())


def candidates(text):
    found = []
    for category, pattern in PATTERNS.items():
        for line in text.splitlines():
            match = re.search(pattern, line, re.I)
            if match:
                start = max(0, match.start()-180)
                found.append({'category': category, 'supporting_excerpt': line[start:start+650],
                              'review_status': 'candidate_needs_review',
                              'claim_type': 'school_website_self_description_not_verified_practice'})
                break
    return found


def get(url):
    with urlopen(Request(url, headers={'User-Agent': AGENT+'/0.1 (public school research)'}), timeout=20) as response:
        final = response.url
        if urlsplit(final).netloc != urlsplit(url).netloc:
            raise ValueError('Cross-host redirect requires permission review')
        raw = response.read(2_000_001)
        if len(raw)>2_000_000: raise ValueError('Page too large')
        return raw.decode(response.headers.get_content_charset() or 'utf-8', errors='replace'), final


@task(persist_result=False)
def collect(code, name, url, folder):
    now = datetime.now(timezone.utc).isoformat()
    base = {'school_unit_code': code, 'school_name': name, 'source_url': url,
            'retrieved_at': now, 'scope_status': 'unit_scope_needs_review',
            'collection_scope': 'registered_landing_page_only', 'method_version': 'website_candidates_v1'}
    origin = urlsplit(url)
    robots_url = f'{origin.scheme}://{origin.netloc}/robots.txt'
    base['robots_url'] = robots_url
    try:
        try:
            robots, _ = get(robots_url)
            (folder/f'{code}_robots.txt').write_text(robots)
            parser = RobotFileParser(); parser.parse(robots.splitlines())
            if not parser.can_fetch(AGENT,url):
                return {**base,'collection_status':'robots_disallowed'}, []
            delay = parser.crawl_delay(AGENT) or parser.crawl_delay('*') or 1
            if delay > 10:
                return {**base,'collection_status':'crawl_delay_requires_manual_plan'}, []
            time.sleep(max(1,delay))
            base['permission_status'] = 'robots_allows_target_terms_not_reviewed'
        except HTTPError as exc:
            if exc.code != 404: raise
            base['permission_status'] = 'robots_not_found_terms_not_reviewed'
            time.sleep(1)
        html, final = get(url)
        parser = Text(); parser.feed(html); text = parser.text()
        (folder/f'{code}_page.txt').write_text(text, encoding='utf-8')
        rows = [{**base,**row,'source_url':final} for row in candidates(text)]
        return {**base,'collection_status':'fetched_needs_review','candidate_count':len(rows)}, rows
    except Exception as exc:
        return {**base,'collection_status':'collection_failed_needs_review','error_type':type(exc).__name__}, []


@flow(name='school-website-focus-pilot', persist_result=False, log_prints=True)
def website_pilot():
    raise RuntimeError('Deprecated focus collector disabled; use contextual approach review and DuckDB batch loading.')
    folder = ROOT/'outputs/website_focus_pilot'; folder.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(ROOT/'.state/schools.sqlite') as conn:
        schools = conn.execute('select school_unit_code,name,website from schools order by school_unit_code').fetchall()
    pilot = {'98760751','36066067','23498302'}
    coverage, evidence = [], []
    for code,name,url in schools:
        if code in pilot and url:
            status, rows = collect(code,name,url,folder); coverage.append(status); evidence.extend(rows)
        else:
            coverage.append({'school_unit_code':code,'school_name':name,'source_url':url,
                             'collection_status':'not_reviewed' if url else 'missing_registered_website'})
    for table, rows in [('school_focus_coverage',coverage),('school_focus_evidence',evidence)]:
        (folder/f'{table}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    # Distinct pipeline and tables: official data is not replaced.
    resources = [dlt.resource(coverage,name='school_focus_coverage',write_disposition='replace')]
    if evidence:
        resources.append(dlt.resource(evidence,name='school_focus_evidence',write_disposition='replace'))
    pipeline = dlt.pipeline(pipeline_name='school_website_focus',
        destination=dlt.destinations.sqlalchemy(f"sqlite:///{ROOT / '.state/schools.sqlite'}"),
        dataset_name='main', pipelines_dir=str(ROOT/'.state/dlt_website'))
    result = pipeline.run(resources); result.raise_on_failed_jobs()
    print({'coverage':len(coverage),'candidate_evidence':len(evidence),
           'pilot_statuses':[(r['school_unit_code'],r['collection_status']) for r in coverage if r['school_unit_code'] in pilot]})


if __name__ == '__main__':
    website_pilot()
