"""Load the second-pass decisions Amna reviewed on 18 Nov 2026 (doc 'Second pass: missed approaches')."""
import csv, json, sys, collections, hashlib, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent; P = HERE.parent
sys.path.insert(0, str(P / 'single_run_20261103')); sys.path.insert(0, '/home/user/proj'); sys.path.insert(0, str(HERE))
from labels import REVIEWED, NOCLEAR
from school_pipeline.approach_migration import validate_records
from school_pipeline.approach_batch import append_batch
DATE = '2026-11-18'; TAG = f'Second pass, reviewed by Amna ({DATE})'; DB = '/home/user/proj/.state/schools.duckdb'
rows = json.load(open(HERE / 'review_rows.json'))
SKIP = {('18053776', 'Support, inclusion, or wellbeing emphasis')}            # Djurö: staff PBS training only (Amna)
DROP_B = {'10311303', '39130058', '42434583', '59975651', '40467992|Support, inclusion, or wellbeing emphasis', '80612612'}  # judgement rows decided No
SUB = {'86440798':'Montessori (authorised by Svenska Montessoriförbundet)','57184925':'Violin orchestra school for all years 1–3','21346638':'Nacka music classes, years 4–6',
 '22513261':'El Sistema string orchestra for all pupils','18064456':'El Sistema wind instruments in school time','78808043|A':'Rhythmics on timetable for all, with Kulturskolan',
 '44673074':'Erasmus+ accredited','11193969':'Erasmus+ exchanges','12187987':'Erasmus and Nordplus exchanges','92127007':'Erasmus+ project','61686233':'Nordplus and Erasmus+ exchanges',
 '33922950':'Erasmus projects','75401552|L':'Erasmus+ accredited; exchanges','45986032':'Finnish-language classes F–6','48760074':'Erasmus+ pupil exchanges, years 7–9','71669600':'English-language profile',
 '39568857':'Bornholmsmodellen','43869172':'Sport track, years 6–9','41507895':'Bornholmsmodellen (F-class)','11777750|O':'Bornholmsmodellen','12801932':'Bornholmsmodellen','12757193':'Football profile, years 3–5',
 '45364437':'Outdoor lessons in nearby nature','38758770':'Outdoor teaching days (F-class only)','19353396':'Green areas used for outdoor teaching','93968806':'Meadow and forest used for learning',
 '98760751':'Local setting integrated in teaching','57368693':'Nature and local setting used in teaching','52064811':'Nature used in teaching','43289917':'Weekly outdoor day (F-class only)',
 '29096335':'Theme work integrating subjects','32585503':'Cross-subject themes','41584790':'Thematic, cross-subject teaching','28184857':'Theme work integrating subjects','31903219':'Thematic work on sustainable learning',
 '11777750|P':'Cross-subject themes and projects','15331669':'Cross-subject projects in all years','26804905':'Multi-week themes','72378947|P':'Projects and cross-subject themes','59900714':'Cross-subject themes',
 '22847273':'Cross-subject work across stages','78808043|P':'Storyline','68812584':'MVP (years 4–6)','61184554':'PBS (positive behaviour support)','57228484':'MVP and Tåget','62862066':'Olweus','24716970|S':'MVP (years 4–9)',
 '85777315':'Olweus','32965692':'Friends','77314942':'Trivselledare','15968847':'PAX','37416253':'MVP on timetable','93320132':'Trivselledare','11777750|S':'PAX','69195602':'Olweus (certified)','10657244':'MVP',
 '73272488':'Trivselledare','40175889':'Trivselledare','45104329':'Tåget','75401552|S':'Olweus','46706680':'Special teaching groups (F–6 and 7–9)','72378947|S':'Weekly Olweus lessons','32479095':'Olweus',
 '97400863':'Special teaching group','42912378':'Trivselledare','87382179':'IBIS',
 '43632318':'Kulturskolan and El Sistema collaboration','26281697':'Football and dance profiles (years 5–9 unit)','35311563':'Pupil-run business project (Glassfabriken)','43138370':'Thematic, cross-subject teaching when suitable',
 '34625544':'Health profile with much outdoor time','84585645':'Cross-subject, thematic teaching','45133950':'Thematic work increasing with age','57467562':'Theme work','13954336':'Cross-subject teaching','82854505':'Cross-subject teaching','10661388':'Cross-subject teaching'}
ab = {'Arts and creative learning':'A','Language, international, or intercultural profile':'L','Other stated profile':'O','Project- or inquiry-based learning':'P','Support, inclusion, or wellbeing emphasis':'S','Outdoor, nature, or place-based learning':'U','Alternative pedagogy':'X'}
def title(u):
    try: return json.load(open(HERE / 'text' / (hashlib.sha1(u.encode()).hexdigest() + '.json'))).get('title') or ''
    except Exception: return ''
E, C, n = [], [], collections.Counter()
for r in rows:
    sid, cat = r['school_id'], r['category']
    if (sid, cat) in SKIP or sid in DROP_B or f'{sid}|{cat}' in DROP_B: continue
    if r['group'] == 'B' and r['category'] == 'Project- or inquiry-based learning' or r['group'] != 'B' or sid in ('43632318','26281697','35311563','43138370','34625544'):
        pass
    if r['group'] == 'C':
        sub = 'Grön Flagg (sustainability)' if 'hållbar utveckling' not in r['quote'] and sid not in ('18193338',) else 'Grön Flagg; Skola för hållbar utveckling'
    else:
        sub = SUB.get(f'{sid}|{ab[cat]}') or SUB[sid]
    lvl = 'Explicit' if r['level'] == 'E' else 'Supported'
    n[sid] += 1; k = f'{sid}_{n[sid]:02d}'
    note = {'A': 'pre-sorted likely yes', 'B': 'judgement call decided by Amna', 'C': 'Grön Flagg / Skola för hållbar utveckling counted as Other stated profile (Amna agreed)'}[r['group']]
    if sid in ('84585645','45133950','57467562','13954336','82854505','10661388'): note = 'Amna: give both codes, Alternative pedagogy and Project'
    E.append(dict(evidence_id=f'ae_sp_{k}', school_id=sid, source_url=r['url'], page_title=r['title'] or title(r['url']) or r['url'], accessed_date=DATE, quoted_text=r['quote'], evidence_type='School webpage',
                  interpretation_note=f"{TAG}: {r['reading']} Page rendered in a browser and scrolled on {DATE}."))
    C.append(dict(code_id=f'ac_sp_{k}', school_id=sid, category=cat, subcategory=sub, coding_level=lvl, confidence='High' if lvl == 'Explicit' else 'Medium', evidence_id=f'ae_sp_{k}',
                  coder_note=f'{TAG}; {note}. Website claim, not independently verified practice.', review_status='Reviewed'))
validate_records(E, C); CH = HERE / 'load'; CH.mkdir(exist_ok=True)
(CH / 'Approach_evidence.staged.json').write_text(json.dumps(E, ensure_ascii=False, indent=2) + '\n'); (CH / 'Approach_codes.staged.json').write_text(json.dumps(C, ensure_ascii=False, indent=2) + '\n')
if '--dry' in sys.argv: print(len(E), len(C), len(n)); sys.exit()
if not (CH / 'load_validation.json').exists():
    rep = append_batch(str(CH), DB); assert rep['status'] == 'PASSED', rep
con = duckdb.connect(DB)
log = [dict(school_id=c['school_id'], code_id=c['code_id'], change='added', detail=f"{c['category'].split(',')[0]}: {c['subcategory']} ({c['coding_level']})") for c in C]
for cid, in con.execute("select code_id from Approach_codes where school_id='47705565' and category='Outdoor, nature, or place-based learning' and subcategory like '%Grön Flagg%'").fetchall():
    con.execute("update Approach_codes set category='Other stated profile', coder_note=coder_note || ' | Moved to Other stated profile 2026-11-18 so all Grön Flagg codes match (Amna).' where code_id=?", [cid])
    log.append(dict(school_id='47705565', code_id=cid, change='category changed', detail='Outdoor -> Other stated profile (Grön Flagg)'))
codes = collections.Counter(x[0] for x in con.execute('select school_id from Approach_codes').fetchall())
led = list(csv.DictReader(open(P / 'county_progress_20261118_after_dq3.csv'))); changed = {}
for x in led:
    has = codes[x['school_id']] > 0; st = x['review_state']
    new = REVIEWED if has and st != REVIEWED else (NOCLEAR if not has and st == REVIEWED else None)
    if new: changed[x['school_id']] = new; x.update(review_state=new, batch_reference='approach_county_review/second_pass_20261118', note=f'{TAG}: {st} -> {new}. | Earlier: ' + x['note'][:300])
with open(P / 'county_progress_20261118_after_sp.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(led[0])); w.writeheader(); w.writerows(led)
seed = '/home/user/proj/dbt/seeds/review_labels.csv'; srows = list(csv.DictReader(open(seed)))
for s in srows:
    if s['school_id'] in changed: s.update(review_state=changed[s['school_id']], batch_reference='second_pass_20261118')
with open(seed, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(srows[0])); w.writeheader(); w.writerows(srows)
with open(HERE / 'changes_20261118_sp.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['school_id', 'code_id', 'change', 'detail']); w.writeheader(); w.writerows(log)
for x in led: assert (x['review_state'] == REVIEWED) == (codes[x['school_id']] > 0), x['school_id']
print(json.dumps(dict(added=len(C), changed=changed, county=collections.Counter(x['review_state'] for x in led), ev=con.execute('select count(*) from Approach_evidence').fetchone()[0], codes=con.execute('select count(*) from Approach_codes').fetchone()[0]), ensure_ascii=False))
