"""Re-fetch live pages for schools to be coded under Rule E and check each quote is still present (18 Nov 2026)."""
import openpyxl, re, html, json, time, urllib.request, urllib.robotparser, urllib.parse, ssl, os
wb = openpyxl.load_workbook('rule_e_review_20261118.xlsx')
yes_rows = {1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,25,27,30,31}
items = []
for i, r in enumerate(wb['Review'].iter_rows(min_row=2, values_only=True), 1):
    if i in yes_rows: items.append((i, r[1], r[2], r[5], r[6]))
for r in wb['Already coded'].iter_rows(min_row=2, values_only=True):
    if r[1] in ('69195602','37416253','39453214','72627865','52217632','37796564'): items.append(('ex', r[0], r[1], r[4], r[5]))
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
rp = {}
def allowed(u):
    h = urllib.parse.urlsplit(u); base = f'{h.scheme}://{h.netloc}'
    if base not in rp:
        p = urllib.robotparser.RobotFileParser(); 
        try: p.parse(urllib.request.urlopen(urllib.request.Request(base + '/robots.txt', headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=20).read().decode('utf8','ignore').splitlines())
        except Exception: p.parse([])
        rp[base] = p
    return rp[base].can_fetch('school-review-bot', u)
norm = lambda s: re.sub(r'\W+', ' ', s).lower().strip()
out = []
for i, name, sid, quote, url in items:
    q = norm(quote.strip('… '))
    if not allowed(url): out.append((i, name, sid, 'robots_disallow', url)); continue
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=30).read().decode('utf8', 'ignore')
    except Exception as e:
        out.append((i, name, sid, f'fetch_error {e}', url)); continue
    s = re.sub(r'(?is)<(script|style).*?</\1>', ' ', b); t = norm(html.unescape(re.sub(r'<[^>]+>', ' ', s)))
    state = 'present' if q in t else ('partly' if q[:60] in t or q[-60:] in t else 'MISSING')
    out.append((i, name, sid, state, url)); time.sleep(1)
json.dump(out, open('recheck_live_20261118.json', 'w'), ensure_ascii=False, indent=1)
for o in out: print(o[:4])
