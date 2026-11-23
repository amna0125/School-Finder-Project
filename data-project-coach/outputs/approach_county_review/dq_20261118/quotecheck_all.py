"""Data-quality check 18 Nov 2026: are ALL coded evidence quotes still on the live source page?"""
import duckdb, random, re, html, ssl, time, json, urllib.request, urllib.robotparser, urllib.parse
db = duckdb.connect('/home/user/proj/.state/schools.duckdb', read_only=True)
ev = db.execute("select e.evidence_id, e.school_id, s.name, e.source_url, e.accessed_date, e.quoted_text from Approach_evidence e join schools s on s.school_unit_code=e.school_id where e.evidence_id in (select evidence_id from Approach_codes) order by e.evidence_id").fetchall()
sample = ev
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt'); rp = {}
def ok(u):
    h = urllib.parse.urlsplit(u); base = f'{h.scheme}://{h.netloc}'
    if base not in rp:
        p = urllib.robotparser.RobotFileParser()
        try: p.parse(urllib.request.urlopen(urllib.request.Request(base + '/robots.txt', headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=20).read().decode('utf8', 'ignore').splitlines())
        except Exception: p.parse([])
        rp[base] = p
    return rp[base].can_fetch('school-review-bot', u)
norm = lambda s: re.sub(r'\W+', ' ', s).lower().strip()
out = []; cache = {}
for eid, sid, name, url, acc, q in sample:
    st = ''
    if not ok(url): st = 'robots_disallow'
    else:
        try:
            if url in cache: b = cache[url]
            else:
              for _a in range(3):
                try: b = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=30).read().decode('utf8', 'ignore'); break
                except Exception as _e:
                  if _a == 2: raise
                  time.sleep(3)
              cache[url] = b
            t = norm(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style).*?</\1>', ' ', b))))
            nq = norm(q); st = 'present' if nq in t else ('partly' if (nq[:50] in t or nq[-50:] in t) else 'missing')
        except Exception as e: st = 'error ' + str(e)[:60]
        time.sleep(1)
    out.append(dict(evidence_id=eid, school_id=sid, name=name, url=url, accessed=acc, quote=q[:200], status=st))
json.dump(out, open('quotecheck_all.json', 'w'), ensure_ascii=False, indent=1)
import collections; print(collections.Counter(o['status'].split(' ')[0] for o in out))
for o in out:
    if o['status'] != 'present': print(o['status'], o['name'], o['accessed'], o['url'], '|', o['quote'][:120])
