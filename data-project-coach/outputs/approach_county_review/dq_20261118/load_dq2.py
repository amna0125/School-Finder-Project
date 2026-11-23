"""Data-quality fixes part 2 (pages found for 2 schools with no saved text). agreed with Amna 18 Nov 2026: Rule E groups for 8 schools that already had other Support codes; Grisslehamn orchestra text gone."""
import csv, json, sys, collections, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = HERE.parent
sys.path.insert(0, str(P / 'single_run_20261103')); sys.path.insert(0, '/home/user/proj')
from labels import REVIEWED, NOCLEAR
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE = '2026-11-18'; TAG = f'Data-quality check with Amna ({DATE})'; CAT = 'Support, inclusion, or wellbeing emphasis'
DB = '/home/user/proj/.state/schools.duckdb'
NEW = [  # registered URLs returned 404; current pages found via municipal navigation 18 Nov 2026
 ('10495223','https://www.botkyrka.se/forskola-och-skola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/tullingebergsskolan','Tullingebergsskolan i Tullinge - Botkyrka kommun','På skolan finns en anpassad grundskola med elever från år ett till år nio samt en särskild undervisningsgrupp med elever från år ett till fem.','Special teaching group (years 1–5)'),
 ('11025388','https://www.ekero.se/forskola-skola/grundskola/skolor-i-ekero-kommun/stenhamraskolan-f-6','Stenhamraskolan F-6 - Ekerö kommun','Skolan har också en särskild undervisningsgrupp med plats för 4-6 elever.','Special teaching group'),
]
E, C = [], []
for sid, url, title, q, sub in NEW:
    eid = f'ae_dq2_{sid}_01'
    E.append(dict(evidence_id=eid, school_id=sid, source_url=url, page_title=title, accessed_date=DATE, quoted_text=q, evidence_type='School webpage',
                  interpretation_note=f'{TAG}: Rule E, standing group named on the school\'s own page. Quote confirmed on the live page {DATE}.'))
    C.append(dict(code_id=f'ac_dq2_{sid}_01', school_id=sid, category=CAT, subcategory=sub, coding_level='Supported', confidence='Medium', evidence_id=eid,
                  coder_note=f'{TAG}; Rule E (standing support group at the unit). Website claim, not independently verified practice.', review_status='Reviewed'))
validate_records(E, C)
CH = HERE / 'load2'; CH.mkdir(exist_ok=True)
(CH / 'Approach_evidence.staged.json').write_text(json.dumps(E, ensure_ascii=False, indent=2) + '\n')
(CH / 'Approach_codes.staged.json').write_text(json.dumps(C, ensure_ascii=False, indent=2) + '\n')
if not (CH / 'load_validation.json').exists():
    rep = append_batch(str(CH), DB); assert rep['status'] == 'PASSED', rep
con = duckdb.connect(DB); log = [dict(school_id=c['school_id'], code_id=c['code_id'], change='added', detail=c['subcategory'] + ' (Supported)') for c in C]
codes = collections.Counter(x[0] for x in con.execute('select school_id from Approach_codes').fetchall())
src = P / 'county_progress_20261118_after_dq.csv'; rows = list(csv.DictReader(open(src))); changed = {}
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
with open(HERE / 'changes_20261118_dq2.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['school_id', 'code_id', 'change', 'detail']); w.writeheader(); w.writerows(log)
for x in rows: assert (x['review_state'] == REVIEWED) == (codes[x['school_id']] > 0), x['school_id']
print(json.dumps(dict(changed=changed, county=collections.Counter(x['review_state'] for x in rows), ev=con.execute('select count(*) from Approach_evidence').fetchone()[0], codes=con.execute('select count(*) from Approach_codes').fetchone()[0]), ensure_ascii=False))
