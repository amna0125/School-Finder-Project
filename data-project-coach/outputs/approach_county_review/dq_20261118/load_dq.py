"""Data-quality fixes agreed with Amna 18 Nov 2026: Rule E groups for 8 schools that already had other Support codes; Grisslehamn orchestra text gone."""
import csv, json, sys, collections, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = HERE.parent
sys.path.insert(0, str(P / 'single_run_20261103')); sys.path.insert(0, '/home/user/proj')
from labels import REVIEWED, NOCLEAR
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE = '2026-11-18'; TAG = f'Data-quality check with Amna ({DATE})'; CAT = 'Support, inclusion, or wellbeing emphasis'
DB = '/home/user/proj/.state/schools.duckdb'
NEW = [  # sid, url, title, quote, subcategory
 ('51210001','https://www.sodertalje.se/skola-och-forskola/grundskola/alla-grundskolor/ronnaskolan/','Ronnaskolan - Södertälje kommun','Ronnaskolan är en tvåparallellig F–9-skola med cirka 600 elever, inklusive anpassad grundskola och en kommunövergripande särskild undervisningsgrupp.','Resource group (municipality-run)'),
 ('71992738','https://www.sodertalje.se/fornbackaskolan','Fornbackaskolan - Södertälje kommun','Här finns både grundskola, anpassad grundskola och en kommunövergripande särskild undervisningsgrupp.','Resource group (municipality-run)'),
 ('17526606','https://fryshuset.se/verksamhet/fryshuset-grundskola-akalla','Fryshuset Grundskola Akalla','Vi erbjuder särskilda undervisningsgrupper och ett engagerat trygghetsteam som tillsammans med våra trygghetsvärdar arbetar för att alla elever ska känna sig säkra och inkluderade.','Special teaching groups'),
 ('17640364','https://grundskola.stockholm/hitta-grundskola/grundskola/spanga-grundskola','Spånga grundskola, 7–9 - Stockholms stad','Vi erbjuder en trygg lärandemiljö med behöriga och engagerade lärare, spetsutbildning i matte och NO, en grupp för nyanlända samt en särskild undervisningsgrupp.','Special teaching group'),
 ('24716970','https://grundskola.stockholm/hitta-grundskola/grundskola/hogalidsskolan','Högalidsskolan, F–9 - Stockholms stad','Det finns 31 klasser inklusive två centrala särskilda undervisningsgrupper.','Special teaching groups (two central groups)'),
 ('25918983','https://www.botkyrka.se/forskola-och-skola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/hammerstaskolan','Hammerstaskolan i Hallunda-Norsborg - Botkyrka kommun','Vi har även en särskild undervisningsgrupp för elever med språkstörning där det går cirka 30 elever från årskurs 1-9.','Special teaching group: language disorder'),
 ('82962565','https://www.huddinge.se/horningsnasskolan/om-skolan','Om Hörningsnässkolan | Huddinge kommun','Den särskilda undervisningsgruppen är en viktig del av verksamheten och bidrar till att möta elevernas olika behov och skapa goda förutsättningar för utveckling och lärande.','Special teaching group'),
 ('85759071','https://www.upplands-bro.se/forskola-och-skola/grundskola/grundskolor-i-upplands-bro/lillsjoskolan.html','Lillsjöskolan - Upplands-Bro','På Lillsjöskolan finns även en kommungemensam resursgrupp som heter Fyren.','Resource group (municipality-run): Fyren'),
]
E, C = [], []
for sid, url, title, q, sub in NEW:
    eid = f'ae_dq_{sid}_01'
    E.append(dict(evidence_id=eid, school_id=sid, source_url=url, page_title=title, accessed_date=DATE, quoted_text=q, evidence_type='School webpage',
                  interpretation_note=f'{TAG}: Rule E, standing group named on the school\'s own page. Quote confirmed on the live page {DATE}.'))
    C.append(dict(code_id=f'ac_dq_{sid}_01', school_id=sid, category=CAT, subcategory=sub, coding_level='Supported', confidence='Medium', evidence_id=eid,
                  coder_note=f'{TAG}; Rule E (standing support group at the unit). Website claim, not independently verified practice.', review_status='Reviewed'))
validate_records(E, C)
CH = HERE / 'load'; CH.mkdir(exist_ok=True)
(CH / 'Approach_evidence.staged.json').write_text(json.dumps(E, ensure_ascii=False, indent=2) + '\n')
(CH / 'Approach_codes.staged.json').write_text(json.dumps(C, ensure_ascii=False, indent=2) + '\n')
if not (CH / 'load_validation.json').exists():
    rep = append_batch(str(CH), DB); assert rep['status'] == 'PASSED', rep
con = duckdb.connect(DB); log = [dict(school_id=c['school_id'], code_id=c['code_id'], change='added', detail=c['subcategory'] + ' (Supported)') for c in C]
for cid, eid in con.execute("select code_id, evidence_id from Approach_codes where school_id='32585503' and subcategory='Recurring school orchestra'").fetchall():
    con.execute('delete from Approach_codes where code_id=?', [cid]); con.execute('delete from Approach_evidence where evidence_id=? and evidence_id not in (select evidence_id from Approach_codes)', [eid])
    log.append(dict(school_id='32585503', code_id=cid, change='removed', detail='Recurring school orchestra: text no longer on the live page (page reviewed 2026-11-12)'))
codes = collections.Counter(x[0] for x in con.execute('select school_id from Approach_codes').fetchall())
src = P / 'county_progress_20261118_after_rule_e.csv'; rows = list(csv.DictReader(open(src))); changed = {}
for x in rows:
    has = codes[x['school_id']] > 0; st = x['review_state']
    new = REVIEWED if has and st != REVIEWED else (NOCLEAR if not has and st == REVIEWED else None)
    if new:
        changed[x['school_id']] = new
        x.update(review_state=new, batch_reference='approach_county_review/dq_20261118', note=f'{TAG}: {st} -> {new}. | Earlier: ' + x['note'][:300])
with open(P / 'county_progress_20261118_after_dq.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
seed = '/home/user/proj/dbt/seeds/review_labels.csv'; srows = list(csv.DictReader(open(seed)))
for s in srows:
    if s['school_id'] in changed: s.update(review_state=changed[s['school_id']], batch_reference='dq_20261118')
with open(seed, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(srows[0])); w.writeheader(); w.writerows(srows)
with open(HERE / 'changes_20261118_dq.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['school_id', 'code_id', 'change', 'detail']); w.writeheader(); w.writerows(log)
for x in rows: assert (x['review_state'] == REVIEWED) == (codes[x['school_id']] > 0), x['school_id']
print(json.dumps(dict(changed=changed, county=collections.Counter(x['review_state'] for x in rows), ev=con.execute('select count(*) from Approach_evidence').fetchone()[0], codes=con.execute('select count(*) from Approach_codes').fetchone()[0]), ensure_ascii=False))
