"""Second pass 18 Nov 2026: scan browser-rendered pages for codebook terms; keep hits in categories (or named programmes) not yet coded for that school."""
import json, re, glob, hashlib, collections, duckdb, unicodedata
plan = json.load(open('plan.json')); disc = json.load(open('discovered.json')) if glob.glob('discovered.json') else {}
db = duckdb.connect('/home/user/proj/.state/schools.duckdb', read_only=True)
coded = collections.defaultdict(list)
for s, c, sub in db.execute('select school_id, category, subcategory from Approach_codes').fetchall(): coded[s].append((c, sub or ''))
names = dict(db.execute('select school_unit_code, name from schools').fetchall())
CAT = {
 'Alternative pedagogy': [('strong', r'montessori\w*|waldorf\w*|steinerpedagog\w*|reggio emilia\w*|freinet\w*|i ur och skur')],
 'Outdoor, nature, or place-based learning': [('strong', r'utomhuspedagog\w*|uteundervisning|uteklassrum\w*|utomhusundervisning|utomhuslektion\w*|naturskol\w*|friluftsdag\w*|utedag\w*|outdoor (?:learning|education|classroom)'),
                                              ('weak', r'(?:skogen|naturen|närområdet|närmiljön)[^.]{0,60}(?:undervisning|lärande|lektion)|(?:undervisning|lektioner)[^.]{0,40}(?:utomhus|ute i)')],
 'Arts and creative learning': [('strong', r'musikklass\w*|musikprofil\w*|dansprofil\w*|estetisk\w* profil|kulturprofil\w*|el sistema|körklass\w*|teaterprofil\w*|musikinriktning|dansinriktning|bildprofil'),
                                ('weak', r'kulturskol\w*|orkester|skolkör\w*|drama på schemat|musikal\w*')],
 'Project- or inquiry-based learning': [('strong', r'ämnesövergripande|tematisk\w* (?:undervisning|arbete|arbetssätt)|temaarbete|projektbaserat?\w*|problembaserat?\w*|storyline|units? of inquiry|inquiry[- ]based|entreprenöriell\w* lärande'),
                                        ('weak', r'\btema\w*|projektarbete\w*|undersökande arbetssätt')],
 'Language, international, or intercultural profile': [('strong', r'tvåspråkig\w*|bilingual|engelskspråkig\w*|undervisning(?:en)? på engelska|ib world school|international baccalaureate|\bpyp\b|\bmyp\b|erasmus\w*|\bclil\b|finskspråkig\w*|språkprofil\w*|språkbad'),
                                                       ('weak', r'internationell\w* (?:profil|inriktning|skola)|engelska från (?:förskoleklass|åk|årskurs) ?[1F]')],
 'Support, inclusion, or wellbeing emphasis': [('prog', r'\bpax\b|olweus\w*|trivselledar\w*|trivselprogram\w*|\bibis\b|positivt beteendestöd|\bpbs\b|generation pep|\bmvp\b|mentorer i våldsprevention|\btåget\b|\bkiva\b|\bfriends\b|livsviktigt|superschysst|hälsoprofil\w*|särskild\w* undervisningsgrupp\w*|resursklass\w*|resursgrupp\w*')],
 'Other stated profile': [('strong', r'idrottsprofil\w*|fotbollsprofil\w*|spetsutbildning\w*|matematikprofil\w*|naturvetenskaplig\w* profil|no-profil|teknikprofil\w*|singaporematematik|singapore­matematik|bornholmsmodellen|schackprofil|hockeyprofil|ridprofil|programmeringsprofil|idrottsinriktning|fotbollsinriktning|spetsklass\w*|grön flagg|skola för hållbar utveckling'),
                          ('weak', r'\w+profil(?:en)?\b')],
}
GENERIC_PROFILE = re.compile(r'grafisk\w* profil|uppdaterad profil|profilbild|vår profil$', re.I)
def norm(s): return unicodedata.normalize('NFKC', s)
def sentences(t):
    t = norm(t)
    for m in re.finditer(r'[^.!?]{20,400}[.!?]', t): yield m.group(0).strip()
def tok(name): return [w for w in re.findall(r'\w+', name.lower()) if len(w) > 3 and w not in ('skola', 'skolan', 'grundskola', 'international', 'school', 'friskola', 'skolor')]
out = {}
for sid, s in plan.items():
    name = names.get(sid) or s.get('name') or ''; toks = tok(name) or tok(s.get('name') or '')
    pages = []
    for u in s['urls'] + disc.get(sid, []):
        f = f'text/{hashlib.sha1(u.encode()).hexdigest()}.json'
        try: r = json.load(open(f))
        except Exception: continue
        if r.get('status') != 200 or not r.get('text'): continue
        t = r['text']; own = any(w in (r.get('title', '') + ' ' + (r.get('final') or u)).lower() for w in toks) or any(w in r.get('final', u).lower() for w in toks)
        pages.append((r.get('final') or u, r.get('title', ''), t, own))
    if not pages: continue
    codcats = {c for c, _ in coded[sid]}; subs = ' '.join(sub.lower() for _, sub in coded[sid])
    hits = collections.defaultdict(list)
    for url, title, text, own in pages:
        for sent in sentences(text):
            if not own and not any(w in sent.lower() for w in toks): continue   # shared page: only sentences naming the school (rule B)
            if '@' in sent or re.search(r'\d{2,4}[- ]\d{2,3} ?\d{2} ?\d{2}', sent): continue
            for cat, pats in CAT.items():
                for strength, p in pats:
                    m = re.search(p, sent, re.I)
                    if not m: continue
                    term = m.group(0).lower()
                    if cat == 'Other stated profile' and strength == 'weak' and GENERIC_PROFILE.search(sent): continue
                    if cat == 'Support, inclusion, or wellbeing emphasis':
                        key = term.split()[0][:6]
                        if key in subs or ('särskild' in term and re.search('special|resource|group|studio', subs)): continue
                    elif cat in codcats: continue
                    if not any(h['sent'] == sent for h in hits[cat]):
                        hits[cat].append(dict(sent=sent[:350], url=url, own=own, strength=strength, term=term))
    if hits: out[sid] = dict(name=name, state=s['state'], coded=[f'{c.split(",")[0]}: {sub}' for c, sub in coded[sid]], hits={c: v[:4] for c, v in hits.items()})
json.dump(out, open('candidates_raw.json', 'w'), ensure_ascii=False, indent=1)
cnt = collections.Counter(); st = collections.Counter()
for v in out.values():
    for c, hs in v['hits'].items(): cnt[c] += 1; st[max((h['strength'] for h in hs), key=lambda x: {'weak': 0, 'strong': 1, 'prog': 2}[x])] += 1
print(len(out), 'schools with uncoded hits'); print(cnt); print(st)
