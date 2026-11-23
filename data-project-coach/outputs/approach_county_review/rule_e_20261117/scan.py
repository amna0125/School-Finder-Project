"""Rule E keyword scan (17 Nov 2026): find statements about resource groups / special teaching groups
in the saved page text of all 762 schools. Produces candidates for Amna's yes/no review; codes nothing."""
import os, re, csv, json, collections, html
BASE = '/home/user/proj/outputs'
OUT = os.path.dirname(os.path.abspath(__file__))
ledger = {r['school_id']: r for r in csv.DictReader(open(f'{BASE}/approach_county_review/county_progress_20261103_after_manual.csv'))}
import duckdb
db = duckdb.connect('/home/user/proj/.state/schools.duckdb', read_only=True)
codes = collections.defaultdict(list)
for sid, cat, sub in db.execute("select school_id, category, subcategory from Approach_codes").fetchall():
    codes[sid].append(f"{cat.split(',')[0].split(' ')[0]}: {sub}" if sub else cat)
support = {sid for sid, in db.execute("select distinct school_id from Approach_codes where category like 'Support%'").fetchall()}
mun = {r[0]: r[1] for r in db.execute("select school_unit_code, municipality_code from schools").fetchall()}
KW = re.compile(r"(resurs\w*grupp\w*|resurs\w*klass\w*|resursskol\w*|särskild\w* undervisningsgrupp\w*|undervisningsgrupp\w*|liten grupp|lilla gruppen|små(?:\s+undervisnings)?grupper|smågrupp\w*|NPF|neuropsykiatri\w*|autism\w*|språkklass\w*|kommungemensam\w*|integrerad\w* grupp\w*|anpassad\w* grupp\w*)", re.I)
# find text files per school (prefer .txt; fall back to stripped html)
files = collections.defaultdict(dict)
for root, _, fs in os.walk(BASE):
    for f in fs:
        m = re.match(r'(\d{8})_(\d+)\.(txt|html?)$', f)
        if m and m.group(1) in ledger:
            p = os.path.join(root, f)
            files[m.group(1)].setdefault(p.rsplit('.', 1)[0], []).append(p)
def text_of(paths):
    t = [p for p in paths if p.endswith('.txt')]
    p = t[0] if t else paths[0]
    s = open(p, encoding='utf8', errors='ignore').read()
    if not t:
        s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', s); s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.sub(r'\s+', ' ', s), p
rows = []
for sid in ledger:
    hits = {}
    for stem, paths in files.get(sid, {}).items():
        s, p = text_of(paths)
        for m in KW.finditer(s):
            a = max(s.rfind('. ', 0, m.start()) + 2, m.start() - 220); b = s.find('. ', m.end()); b = len(s) if b < 0 else min(b + 1, m.end() + 220)
            snip = s[a:b].strip()
            key = re.sub(r'\W+', '', snip.lower())[:120]
            if key not in hits: hits[key] = (m.group(0), snip, p)
    if hits:
        L = ledger[sid]
        rows.append(dict(school_id=sid, name=L['official_directory_name'], review_state=L['review_state'],
                         has_support_code=sid in support, codes='; '.join(codes.get(sid, [])),
                         keywords=', '.join(sorted({h[0].lower() for h in hits.values()})),
                         n_snippets=len(hits), snippets=' || '.join(h[1] for h in list(hits.values())[:6]),
                         files=' | '.join(sorted({os.path.relpath(h[2], BASE) for h in hits.values()}))))
print('schools with saved text', len(files), 'of', len(ledger), '; with hits', len(rows))
print('already Support', sum(r['has_support_code'] for r in rows), '; without Support', sum(not r['has_support_code'] for r in rows))
print(collections.Counter(r['review_state'] for r in rows if not r['has_support_code']))
with open(f'{OUT}/candidates_all.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
missing = sorted(set(ledger) - set(files))
json.dump(missing, open(f'{OUT}/no_saved_text.json', 'w'))
print('no saved text:', len(missing))
