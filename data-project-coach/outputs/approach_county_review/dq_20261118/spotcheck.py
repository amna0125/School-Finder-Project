"""Data-quality spot-check 18 Nov 2026: 30 random 'No clear evidence' schools, live pages scanned for codebook terms."""
import csv, json, random, re, html, ssl, time, urllib.request, urllib.robotparser, urllib.parse, glob, os, sys
P = '/home/user/proj/outputs/approach_county_review'
sys.path.insert(0, P + '/rule_e_20261117')
rows = list(csv.DictReader(open(f'{P}/county_progress_20261118_after_rule_e.csv')))
nc = [r for r in rows if r['review_state'] == 'No clear evidence in scoped review']
random.seed(20261118); sample = random.sample(nc, 30)
# saved source URLs per school
urls = {}
for j in glob.glob(f'{P}/fresh/*.json'):
    d = json.load(open(j))
    if 'school_id' not in d: continue
    urls.setdefault(d['school_id'], []).extend(p.get('source_url') for p in d.get('pages', []) if p.get('source_url'))
for l in open(f'{P}/setting_20261104/collection.jsonl'):
    d = json.loads(l); urls.setdefault(d['school_id'], []).extend(p.get('source_url') for p in d.get('pages', []) if p.get('source_url'))
for c in glob.glob(f'{P}/single_run_20261103/**/collection_log.csv', recursive=True):
    for r in csv.DictReader(open(c)):
        if r.get('final_url'): urls.setdefault(r['school_id'], []).append(r['final_url'])
KW = re.compile(r'(montessori|waldorf|steiner|reggio|freinet|utomhuspedagog\w*|uteklassrum|naturskol\w*|friluftsliv|utedag\w*|musikklass\w*|musikprofil|kulturskol\w*|estetisk\w* profil|dansprofil|drama|tvåspråkig\w*|bilingual|engelskspråkig\w*|international\w*|IB\b|tematisk\w*|ämnesövergripande|projektarbet\w*|entreprenöri\w*|resurs\w*(?:grupp|klass|skol)\w*|särskild\w* undervisningsgrupp\w*|olweus|trivselledar\w*|PAX\b|IBIS|PBS\b|MVP\b|Generation Pep|idrottsprofil|fotbollsprofil|\w*profil\b|spetsutbildning|programmering|spetsklass)', re.I)
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt'); rp = {}
def ok(u):
    h = urllib.parse.urlsplit(u); base = f'{h.scheme}://{h.netloc}'
    if base not in rp:
        p = urllib.robotparser.RobotFileParser()
        try: p.parse(urllib.request.urlopen(urllib.request.Request(base + '/robots.txt', headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=20).read().decode('utf8', 'ignore').splitlines())
        except Exception: p.parse([])
        rp[base] = p
    return rp[base].can_fetch('school-review-bot', u)
def get(u):
    b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=30).read().decode('utf8', 'ignore')
    b = re.sub(r'(?is)<(script|style|nav|header|footer)\b.*?</\1>', ' ', b)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', b)))
out = []
for r in sample:
    sid = r['school_id']; us = list(dict.fromkeys(u for u in urls.get(sid, []) if u))[:4]
    res = dict(school_id=sid, name=r['official_directory_name'], note=r['note'][:250], pages=[])
    for u in us:
        if not ok(u): res['pages'].append(dict(url=u, status='robots')); continue
        try: t = get(u)
        except Exception as e: res['pages'].append(dict(url=u, status=f'error {str(e)[:60]}')); continue
        hits = []
        for m in KW.finditer(t):
            a = max(0, m.start() - 140); s = t[a:m.end() + 140]
            s = re.sub(r'\S+@\S+', '[email]', s)
            if not any(s[150:200] in h for h in hits): hits.append(s)
        res['pages'].append(dict(url=u, status='ok', mentions_name=r['official_directory_name'].split()[0].lower() in t.lower(), hits=hits[:12]))
        time.sleep(1)
    out.append(res)
json.dump(out, open('spotcheck_raw.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), sum(1 for o in out if not o['pages']))
