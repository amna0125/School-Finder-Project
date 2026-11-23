"""Resumable source refresh only; never writes live database or legacy tables."""
import concurrent.futures
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from prefect import flow
from school_pipeline.website_county import page, relevant_links
from school_pipeline.website_focus import Text

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/approach_county_review/fresh'

class Title(HTMLParser):
    def __init__(self):
        super().__init__(); self.active = False; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'title': self.active = True
    def handle_endtag(self, tag):
        if tag == 'title': self.active = False
    def handle_data(self, data):
        if self.active: self.parts.append(data)


def collect(row):
    code = row['school_id']; target = OUT / (code + '.json')
    if target.exists(): return json.loads(target.read_text())
    record = {'school_id': code, 'school_name': row['school_name'],
              'registered_url': row['registered_url'], 'pages': [], 'errors': [],
              'review_status': 'Requires review', 'approach_codes_assigned': False,
              'selection_rationale': row['selection_rationale']}
    old = json.loads((ROOT / 'outputs/website_county' / (code + '.json')).read_text())
    urls = list(dict.fromkeys(p['source_url'] for p in old.get('pages', [])))
    if not urls and row['registered_url']: urls = [row['registered_url']]
    if not urls:
        record['collection_status'] = 'missing_registered_website'
    elif old.get('terms_urls'):
        record.update(collection_status='terms_review_required', terms_urls=old['terms_urls'])
    else:
        for url in urls[:3]:
            try:
                final, html, checks = page(url, OUT)
                accessed = datetime.now(timezone.utc).isoformat()
                title = Title(); title.feed(html)
                title_text = ' '.join(''.join(title.parts).split())
                text = Text(); text.feed(html)
                _, terms = relevant_links(final, html)
                # Store source text for contextual review, not HTML/media or employee datasets.
                name = f'{code}_{len(record["pages"])}.txt'
                (OUT / name).write_text(text.text(), encoding='utf-8')
                record['pages'].append({'requested_url': url, 'source_url': final,
                    'page_title': title_text or None, 'accessed_at': accessed,
                    'accessed_date': accessed[:10], 'text_file': name,
                    'robots_checks': checks, 'terms_urls': terms,
                    'permission_status': 'terms_review_required' if terms else 'no_terms_link_detected_not_legal_clearance'})
                if terms:
                    record['terms_urls'] = terms
                    break
            except Exception as exc:
                record['errors'].append({'url': url, 'error': str(exc)[:350],
                    'attempted_at': datetime.now(timezone.utc).isoformat()})
        record['collection_status'] = 'fetched_requires_context_review' if record['pages'] else 'inaccessible_requires_review'
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return record

@flow(name='refresh-county-approach-sources', log_prints=True)
def run(seconds=540):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in (ROOT / 'outputs/approach_county_review/collection_log.jsonl').read_text().splitlines()]
    deadline = time.monotonic() + seconds
    # Bounded waves mean a time-limited run can safely resume without refetching checkpoints.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for start in range(0, len(rows), 6):
            if time.monotonic() >= deadline: break
            list(pool.map(collect, rows[start:start + 6]))
    from collections import Counter
    saved = [json.loads(p.read_text()) for p in OUT.glob('*.json') if p.stem.isdigit()]
    summary = {'directory_units': len(rows), 'checkpointed_units': len(saved),
        'not_attempted_this_refresh': len(rows)-len(saved),
        'collection_statuses': dict(Counter(r['collection_status'] for r in saved)),
        'fresh_pages': sum(len(r['pages']) for r in saved),
        'new_approach_codes': 0, 'live_database_modified': False,
        'updated_at': datetime.now(timezone.utc).isoformat()}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
    print(summary)

if __name__ == '__main__': run()
