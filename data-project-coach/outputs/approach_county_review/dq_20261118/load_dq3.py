"""Decisions with Amna on the 7 'claim gone' schools (18 Nov 2026 evening). Amna re-checked the pages in a normal browser."""
import csv, json, sys, collections, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = HERE.parent
sys.path.insert(0, str(P / 'single_run_20261103')); sys.path.insert(0, '/home/user/proj')
from labels import REVIEWED, NOCLEAR
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE = '2026-11-18'; TAG = f'Quote check with Amna ({DATE})'; DB = '/home/user/proj/.state/schools.duckdb'
E = [dict(evidence_id='ae_dq3_46518352_01', school_id='46518352', source_url='https://www.norrtalje.se/info/barn-och-skola/grundskola/grundskolor/elmsta-skola/var-skola/', page_title='Vår skola - Elmsta skola | Norrtälje kommun',
          accessed_date=DATE, quoted_text='Ett av våra verktyg för att skapa glädje, trivsel och trygghet är ”PAX i skolan”.', evidence_type='School webpage',
          interpretation_note=f'{TAG}: found by Amna; PAX is a named programme (same as other PAX schools). Quote confirmed on the live page {DATE}.')]
C = [dict(code_id='ac_dq3_46518352_01', school_id='46518352', category='Support, inclusion, or wellbeing emphasis', subcategory='PAX', coding_level='Supported', confidence='Medium',
          evidence_id='ae_dq3_46518352_01', coder_note=f'{TAG}; named wellbeing programme. Website claim, not independently verified practice.', review_status='Reviewed')]
validate_records(E, C); CH = HERE / 'load3'; CH.mkdir(exist_ok=True)
(CH / 'Approach_evidence.staged.json').write_text(json.dumps(E, ensure_ascii=False, indent=2) + '\n'); (CH / 'Approach_codes.staged.json').write_text(json.dumps(C, ensure_ascii=False, indent=2) + '\n')
if not (CH / 'load_validation.json').exists():
    rep = append_batch(str(CH), DB); assert rep['status'] == 'PASSED', rep
con = duckdb.connect(DB); log = [dict(school_id='46518352', code_id='ac_dq3_46518352_01', change='added', detail='Support: PAX (Supported)')]
REMOVE = [('60570294', 'Football profile with Hammarby', 'football profile no longer on the page'), ('57368693', 'Trivselprogrammet', 'Trivselprogrammet no longer on the page'),
          ('53133366', 'Entrepreneurial pedagogy', 'pedagogy page removed; the page now names Myrsjö resursskola, which is its own registered unit (90207041, already coded) - Rule B'),
          ('46518352', 'Recurring assemblies with music and drama', 'assemblies text no longer on the page')]
for sid, sub, why in REMOVE:
    for cid, eid in con.execute('select code_id, evidence_id from Approach_codes where school_id=? and subcategory=?', [sid, sub]).fetchall():
        con.execute('delete from Approach_codes where code_id=?', [cid]); con.execute('delete from Approach_evidence where evidence_id=? and evidence_id not in (select evidence_id from Approach_codes)', [eid])
        log.append(dict(school_id=sid, code_id=cid, change='removed', detail=f'{sub}: {why}'))
REF = [('ae_s3c_25090415_01', 'https://www.varmdo.se/barnochutbildning/skolbarn/alltomgrundskolan/grundskolorivarmdokommun/fagelviksskola.4.2d09c46d1850f82301f8f86.html', 'Fågelviks skola - Värmdö kommun', 'Vi använder ofta vår närliggande skog för lek och lärande.'),
       ('ae_sr_84585645_02', 'https://hagaskolan.se/', 'Hagaskolan – Waldorfskolan i Norrort', 'Med en friluftsdag i månaden samt dagliga fysiska aktiviteter stimuleras eleverna i linje med vad modern forskning stipulerar.')]
for eid, url, title, q in REF:
    old = con.execute('select quoted_text from Approach_evidence where evidence_id=?', [eid]).fetchone()[0]
    con.execute("update Approach_evidence set source_url=?, page_title=?, quoted_text=?, accessed_date=?, interpretation_note=interpretation_note || ? where evidence_id=?",
                [url, title, q, DATE, f' | {TAG}: claim confirmed on the live page (Amna); quote refreshed. Earlier: {old[:160]}', eid])
    log.append(dict(school_id=eid.split('_')[2], code_id=eid, change='quote refreshed', detail=q[:120]))
codes = collections.Counter(x[0] for x in con.execute('select school_id from Approach_codes').fetchall())
rows = list(csv.DictReader(open(P / 'county_progress_20261118_after_dq.csv'))); changed = {}
for x in rows:
    has = codes[x['school_id']] > 0; st = x['review_state']
    new = REVIEWED if has and st != REVIEWED else (NOCLEAR if not has and st == REVIEWED else None)
    if new: changed[x['school_id']] = new; x.update(review_state=new, batch_reference='approach_county_review/dq_20261118', note=f'{TAG}: {st} -> {new}. | Earlier: ' + x['note'][:300])
with open(P / 'county_progress_20261118_after_dq3.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
seed = '/home/user/proj/dbt/seeds/review_labels.csv'; srows = list(csv.DictReader(open(seed)))
for s in srows:
    if s['school_id'] in changed: s.update(review_state=changed[s['school_id']], batch_reference='dq_20261118')
with open(seed, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(srows[0])); w.writeheader(); w.writerows(srows)
with open(HERE / 'changes_20261118_dq3.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['school_id', 'code_id', 'change', 'detail']); w.writeheader(); w.writerows(log)
for x in rows: assert (x['review_state'] == REVIEWED) == (codes[x['school_id']] > 0), x['school_id']
print(json.dumps(dict(changed=changed, county=collections.Counter(x['review_state'] for x in rows), ev=con.execute('select count(*) from Approach_evidence').fetchone()[0], codes=con.execute('select count(*) from Approach_codes').fetchone()[0]), ensure_ascii=False))
