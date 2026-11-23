"""Pick one short verbatim quote per candidate (no contact lines) and map its source URL."""
import csv, json, re, glob, os
B = '/home/user/proj/outputs/approach_county_review'
url = {}
for j in glob.glob(f'{B}/fresh/*.json'):
    for p in json.load(open(j)).get('pages', []):
        if p.get('text_file'): url[f'approach_county_review/fresh/{p["text_file"]}'] = p.get('source_url') or p.get('requested_url')
for l in open(f'{B}/setting_20261104/collection.jsonl'):
    for p in json.loads(l).get('pages', []):
        if p.get('text_file'): url['approach_county_review/setting_20261104/' + p['text_file']] = p.get('source_url')
for c in glob.glob(f'{B}/single_run_20261103/**/collection_log.csv', recursive=True):
    base = os.path.dirname(c)
    for r in csv.DictReader(open(c)):
        if r['source_file']:
            f = os.path.normpath(os.path.join(base, r['source_file'])).replace('/home/user/proj/outputs/', '')
            url[f.rsplit('.', 1)[0] + '.txt'] = r['final_url'] or r['requested_url']
KW = re.compile(r"(resurs\w*grupp\w*|resurs\w*klass\w*|resursskol\w*|särskild\w* undervisningsgrupp\w*|undervisningsgrupp\w*|liten grupp|lilla gruppen|små(?:\s+undervisnings)?grupper|smågrupp\w*|NPF|neuropsykiatri\w*|autism\w*|språkklass\w*|kommungemensam\w*|integrerad\w* grupp\w*|anpassad\w* grupp\w*)", re.I)
CONTACT = re.compile(r'@|\d{2,4}[- ]\d{2,3}[ -]?\d{2,3}|rektor\b|Rektor ', re.I)
out = {}
for r in csv.DictReader(open(f'{B}/rule_e_20261117/candidates_all.csv')):
    if r['has_support_code'] != 'False': continue
    files = [f for f in r['files'].split(' | ') if f]
    snips = r['snippets'].split(' || ')
    def score(s):
        sc = 0
        if CONTACT.search(s): sc -= 10
        if any(t.lower() in s.lower() for t in r['name'].split()[:1]): sc += 3
        if re.search(r'\b(vi har|skolan har|finns|erbjuder)\b', s, re.I): sc += 2
        if re.search(r'särskild\w* undervisningsgrupp|resurs\w*(grupp|klass|skol)|KSU|KÖSU|RSK', s, re.I): sc += 2
        return sc
    best = sorted(snips, key=score, reverse=True)
    q = best[0].strip()
    m = KW.search(q)
    if m and len(q) > 240:   # trim to whole words around the keyword
        a = max(0, m.start() - 110); b = min(len(q), m.end() + 110)
        q = q[a:b]; q = (q.split(' ', 1)[1] if a else q).rsplit(' ', 1)[0] if b < len(best[0]) else q
        q = ('… ' if a else '') + q + (' …' if b < len(best[0].strip()) else '')
    srcs = [url.get(f, '') for f in files]
    out[r['school_id']] = dict(name=r['name'], state=r['review_state'], codes=r['codes'], keywords=r['keywords'],
                               quote=q, contact_only=score(best[0]) < 0, url=next((u for u in srcs if u), ''), missing_url=[f for f, u in zip(files, srcs) if not u])
json.dump(out, open(f'{B}/rule_e_20261117/quotes.json', 'w'), ensure_ascii=False, indent=1)
print(sum(1 for v in out.values() if v['missing_url']), 'with unmapped files')
