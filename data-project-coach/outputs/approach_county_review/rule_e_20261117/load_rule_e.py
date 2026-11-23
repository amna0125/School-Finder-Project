"""Load Rule E decisions agreed with Amna in the doc 'Rule E review: support groups' (18 Nov 2026).
Adds new Support codes, changes levels, removes codes that fail the tightened standard, updates ledger + dbt seed."""
import csv, json, re, html, ssl, sys, urllib.request, collections, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = HERE.parent
sys.path.insert(0, str(P / 'single_run_20261103')); sys.path.insert(0, '/home/user/proj')
from labels import REVIEWED, NOCLEAR, NOPAGE
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE = '2026-11-18'; TAG = f'Rule E review with Amna ({DATE})'
CAT = 'Support, inclusion, or wellbeing emphasis'
DB = '/home/user/proj/.state/schools.duckdb'
q = json.load(open(HERE / 'quotes.json'))
src = open(HERE / 'build_review.py').read()
ns = {}; exec(src[src.index('fix = {'):src.index("G = {1:")], {'json': json, 'q': q}, ns)
fix, plan = ns['fix'], ns['plan']
fix['72672270'] = 'Biträdande rektor anpassad grundskola, elevhälsoteamet, särskild undervisningsgrupp årskurs F–5'
live = {x[2]: x for x in json.load(open(HERE / 'recheck_live_20261118.json'))}
NEW = {  # sid: (level, subcategory, note)
 **{s: ('S', plan[s][2], plan[s][3]) for s in ['44673074','46616391','92347699','42434583','92284588','83810698','40631085','15080815','24561769','12187987','17287315','77314942','11914814','33794207','58385274','72120589','44046131','45757947','58294404']},
 '96646603': ('E', plan['96646603'][2], 'The page heads the school as a municipal resource school F–9, so the whole profile is support.'),
 '72672270': ('S', 'Special teaching group (F–5 and 6–9)', 'Group named in staff role titles on the school\'s own page; no staff names stored.'),
 '84520303': ('S', plan['84520303'][2], 'Group named in a staff role title on the school\'s own page; no staff names stored.'),
 '62288230': ('S', plan['62288230'][2], 'Group named in a staff role title on the school\'s own page; no staff names stored.'),
 '78508835': ('S', plan['78508835'][2], 'Group named in staff role titles on the school\'s own page; no staff names stored.'),
 '94279206': ('E', 'Resource school (municipality-run)', 'Quote from Sjötorpsskolan\'s page: the resource school is on site. Unit identity from the Skolverket register (same visiting address as Sjötorpsskolan), not from the name. Agreed with Amna.'),
}
REMOVE = {('23617768','Flexible small teaching groups'),('47640376','Individual action plans and learning centre'),('20563782','Differentiated teaching and movement emphasis'),
 ('19377571','Daylong visual supports and accessible learning'),('57755652','Visual support and predictable routines'),('43632318','Structured, accessible teaching and multi-teacher support'),
 ('49762104','Predictable, accessible teacher-led teaching'),('98070480','Tydliggörande pedagogik'),('13582062','Additional teaching support'),('42149666','Multi-teacher system and common lesson structure'),
 ('56568612','Three-teacher model F–6; two-teacher 7–9'),('37556682','Two adults per lesson / two-teacher Swedish'),('51210001','Two-teacher teaching and half-class practical subjects'),
 ('66383692','Smaller groups; on-site resource school')}
TO_S = {('37416253','Additional special teaching group for pupils with greater support needs'),('39453214','Attached lärstudio / special teaching group only'),('72627865','Hearing-impairment classes'),
 ('52217632','Municipal special teaching groups for autism'),('37796564','Regional special teaching groups (RSU); restricted placements')}
TO_E = {('69195602','Municipal special teaching group')}
RENAME = {('82110758','MVP and Agera; special teaching groups'): 'MVP and Agera'}
ctx = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
def title(u):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'school-review-bot'}), context=ctx, timeout=30).read().decode('utf8', 'ignore')
        m = re.search(r'(?is)<title[^>]*>(.*?)</title>', b); return re.sub(r'\s+', ' ', html.unescape(m.group(1))).strip() if m else u
    except Exception: return u
LV = {'E': ('Explicit', 'High'), 'S': ('Supported', 'Medium')}
E, C = [], []
for sid, (lv, sub, note) in NEW.items():
    assert live[sid][3] in ('present',) or sid in ('72672270', '33794207'), (sid, live[sid])
    url = live[sid][4]; eid = f'ae_rule_e_{sid}_01'
    E.append(dict(evidence_id=eid, school_id=sid, source_url=url, page_title=title(url), accessed_date=DATE, quoted_text=fix.get(sid, q[sid]['quote']).strip('… '),
                  evidence_type='School webpage', interpretation_note=f'{TAG}: {note} Quote confirmed on the live page {DATE}.'))
    C.append(dict(code_id=f'ac_rule_e_{sid}_01', school_id=sid, category=CAT, subcategory=sub, coding_level=LV[lv][0], confidence=LV[lv][1], evidence_id=eid,
                  coder_note=f'{TAG}; Rule E (standing support group or resource school at the unit). Website claim, not independently verified practice.', review_status='Reviewed'))
validate_records(E, C)
CH = HERE / 'load'; CH.mkdir(exist_ok=True)
(CH / 'Approach_evidence.staged.json').write_text(json.dumps(E, ensure_ascii=False, indent=2) + '\n')
(CH / 'Approach_codes.staged.json').write_text(json.dumps(C, ensure_ascii=False, indent=2) + '\n')
if not (CH / 'load_validation.json').exists():
    rep = append_batch(str(CH), DB); assert rep['status'] == 'PASSED', rep
con = duckdb.connect(DB)
log = []
def one(sid, sub):
    r = con.execute('select code_id, evidence_id, coding_level from Approach_codes where school_id=? and category=? and subcategory=?', [sid, CAT, sub]).fetchall()
    assert len(r) <= 1, (sid, sub, r); return r[0] if r else None
for sid, sub in sorted(REMOVE):
    r = one(sid, sub)
    if not r: continue
    con.execute('delete from Approach_codes where code_id=?', [r[0]])
    if not con.execute('select count(*) from Approach_codes where evidence_id=?', [r[1]]).fetchone()[0]:
        con.execute('delete from Approach_evidence where evidence_id=?', [r[1]])
    log.append(dict(school_id=sid, code_id=r[0], change='removed', detail=sub))
for sset, (lvl, conf) in ((TO_S, LV['S']), (TO_E, LV['E'])):
    for sid, sub in sorted(sset):
        r = one(sid, sub)
        if r and r[2] != lvl:
            con.execute("update Approach_codes set coding_level=?, confidence=?, coder_note=coder_note || ? where code_id=?", [lvl, conf, f' | {TAG}: level changed from {r[2]} to {lvl} (tightened Rule E).', r[0]])
            log.append(dict(school_id=sid, code_id=r[0], change=f'{r[2]} -> {lvl}', detail=sub))
for (sid, sub), new in RENAME.items():
    r = one(sid, sub)
    if r:
        con.execute("update Approach_codes set subcategory=?, coder_note=coder_note || ? where code_id=?", [new, f' | {TAG}: subcategory narrowed; quote names MVP and Agera only.', r[0]])
        log.append(dict(school_id=sid, code_id=r[0], change='subcategory renamed', detail=f'{sub} -> {new}'))
for c in C: log.append(dict(school_id=c['school_id'], code_id=c['code_id'], change='added', detail=f"{c['subcategory']} ({c['coding_level']})"))
codes = collections.Counter(x[0] for x in con.execute('select school_id from Approach_codes').fetchall())
rows = list(csv.DictReader(open(P / 'county_progress_20261103_after_manual.csv')))
changed = []
for x in rows:
    has = codes[x['school_id']] > 0; st = x['review_state']
    if has and st != REVIEWED: new = REVIEWED
    elif not has and st == REVIEWED: new = NOCLEAR
    else: continue
    changed.append((x['school_id'], st, new))
    x.update(review_state=new, batch_reference='approach_county_review/rule_e_20261117', note=f'{TAG}: {st} -> {new}. | Earlier: ' + x['note'][:300])
with open(P / 'county_progress_20261118_after_rule_e.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
seed = '/home/user/proj/dbt/seeds/review_labels.csv'
srows = list(csv.DictReader(open(seed))); lab = {x['school_id']: x for x in rows}
for s in srows:
    if s['school_id'] in dict((c[0], 1) for c in changed): s.update(review_state=lab[s['school_id']]['review_state'], batch_reference='rule_e_20261117')
with open(seed, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(srows[0])); w.writeheader(); w.writerows(srows)
with open(HERE / 'changes_20261118.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['school_id', 'code_id', 'change', 'detail']); w.writeheader(); w.writerows(log)
for x in rows:
    assert (x['review_state'] == REVIEWED) == (codes[x['school_id']] > 0), x['school_id']
print(json.dumps(dict(added=len(C), removed=sum(1 for l in log if l['change'] == 'removed'), level=sum(1 for l in log if '->' in l['change'] and 'renamed' not in l['change']),
      label_changes=changed, county=collections.Counter(x['review_state'] for x in rows),
      db_evidence=con.execute('select count(*) from Approach_evidence').fetchone()[0], db_codes=con.execute('select count(*) from Approach_codes').fetchone()[0]), ensure_ascii=False, indent=0))
con.close()
