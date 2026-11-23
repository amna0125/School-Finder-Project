"""One-time Batch23 staging; do not rerun after success."""
from pathlib import Path
import csv,json,re,html,hashlib
import duckdb
from outputs.approach_county_review.extract19 import parse
from school_pipeline.approach_migration import validate_records
P=Path('outputs/approach_county_review'); B=P/'batch23_10schools_20261102'; S=B/'sources'; D='2026-11-02'
assert not (B/'Approach_evidence.staged.json').exists()
def dump(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str)+'\n')
rows=list(csv.DictReader((P/'county_progress_20261102_after_batch22.csv').open()))
selection=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]
assert selection==json.loads((P/'next_batch_after_batch22.json').read_text())
ids=[r['school_id'] for r in selection]
assert ids==['37887150','38096510','38394561','38526011','38653015','38661388','38758770','38854084','38935587','38975788']
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 names=['school_unit_code','name','municipality_code','grades_json','website','status','source_extract_date']
 meta=[dict(zip(names,db.execute('select '+','.join(names)+' from schools where school_unit_code=?',[sid]).fetchone())) for sid in ids]
u=dict(nordic='https://nordicinternational.se/nacka',nordic_about='https://nordicinternational.se/nacka/om-skolan/',magelungen='https://magelungen.com/kontaktpersoner/alvsjo/',mag_resource='https://magelungen.com/resursskola/',mag_unit='https://magelungen.com/enheter/stockholm-alvsjo-grundskola/',friskola='https://www.sodertaljefriskola.se',edda='https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/eddaskolan/pa-eddaskolan/valkommen-till-eddaskolan.html',edda_work='https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/eddaskolan/arbetssatt-och-kvalitetsarbete.html',pershagen_old='https://www.sodertalje.se/pershagenskolan.',pershagen='https://www.sodertalje.se/skola-och-forskola/grundskola/alla-grundskolor/pershagenskolan/',broang='https://www.botkyrka.se/broangsskolan',broang_current='https://www.botkyrka.se/forskola-och-skola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/broangsskolan',farsta='https://grundskola.stockholm/hitta-grundskola/grundskola/farsta-grundskola-med-adolf-fredriks-musikklasser',farsta_unit='https://farstagrundskola.stockholm/',farsta_about='https://farstagrundskola.stockholm/det-har-ar-farsta-grundskola/',steninge='https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/steningehojdens-skola/pa-steningehojdens-skola/valkommen-till-steningehojdens-skola.html',steninge_work='https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/steningehojdens-skola/arbetssatt-och-kvalitetsarbete.html',ies='https://engelska.se/our-schools/enskede/',ies_about='https://engelska.se/our-schools/enskede/about-our-school/',tungelsta='https://tungelstaskola.haninge.se/var-skola/',tungelsta_work='https://tungelstaskola.haninge.se/sa-har-jobbar-vi/')
pages=dict(zip(ids,[['nordic','nordic_about'],['magelungen','mag_resource','mag_unit'],['friskola'],['edda','edda_work'],['pershagen_old','pershagen'],['broang','broang_current'],['farsta','farsta_unit','farsta_about'],['steninge','steninge_work'],['ies','ies_about'],['tungelsta','tungelsta_work']]))
notes=dict(zip(ids,[
'Swedish teaching explicitly stated; internationally inspired pedagogy is too broad for a language/international code or named alternative pedagogy. F–9 website vs official1–9; prior inaccessible outcome retained. Requires review if more specific pedagogy evidence emerges.',
'Unit-specific Älvsjö resource-school description; official4–9. Intensive support applies to resource-school placements. Separate behandlingsskola/social-services intervention is not assigned to every pupil. Small groups and staffing are self-reported, not comparable statistics. Registered provider homepage resolved through directory to unit.',
'Explicit language profile and additional Swedish/English teaching time. WebsiteF–9 vs official1–9. No separate support code from ordinary staffing/group statements.',
'Welcome and working-method pages scoped review: ordinary values, peer activities and generic municipal quality work do not establish a distinct approach. Separate anpassad grundskola since2025/26 excluded. F–6 website vs official1–6. No clear evidence within this review, not absence of an approach.',
'Explicit developing technology profile with municipal partners. Other stated profile only; not inquiry/project learning inferred. Developmental wording retained; no claim that a mature pathway exists or all pupils receive extra hours. F–9 website vs official1–9.',
'Named violence-prevention Tåget/MVP programme described on Broängsskolan page for shared Tumba Södra rector-area with Kassmyraskolan. MVP specifically7–9; do not assign separate-school statistics or assume outdoor pedagogy from reserve location. F–9 website vs official1–9.',
'Music/choir profile only selected music classes years4–9, not whole FarstaF–9 population or co-located anpassad provision. School description confirms year range and daily music; directory describes skills-test admission. F-class outdoor provision not coded for official1–9 unit.',
'Welcome and working-method pages scoped review: learning/digital ability/health/feeling focus and general vision lack specific distinctive provision. No firm code. F–9 website vs official1–9. No clear evidence within reviewed pages, not absence.',
'Unit-specific homepage explicitly bilingual with up to50% English teaching, years4–9 matching official range. About page contains erroneous Karlstad history/234 students6–9; exclude that paragraph and do not use counts as official statistics.',
'Our-school and working-method pages scoped review: general inclusion, expectations, facilities and nearby nature insufficient for support/outdoor codes. F–9 website vs official1–9. No clear evidence in reviewed scope; no pupil-survey/application follow-up.'
]))
outcomes={sid:('Uncertain evidence — no firm code' if sid==ids[0] else 'No clear evidence within scoped review' if sid in [ids[3],ids[7],ids[9]] else 'Reviewed approach claims') for sid in ids}
def title(n):return html.unescape(re.sub(r'\s+',' ',re.search(r'<title[^>]*>(.*?)</title>',(S/(n+'.html')).read_text(),re.S|re.I)[1])).strip()
e=[];c=[]
def add(sid,n,quote,cat=None,sub=''):
 assert quote in parse(S/(n+'.html'))[0],(n,quote)
 eid=f'ae_b23_{sid}_{sum(x["school_id"]==sid for x in e)+1:02}'
 e.append(dict(evidence_id=eid,school_id=sid,source_url=u[n],page_title=title(n),accessed_date=D,quoted_text=quote,evidence_type='School webpage',interpretation_note=notes[sid]))
 if cat:c.append(dict(code_id=f'ac_b23_{sid}_01',school_id=sid,category=cat,subcategory=sub,coding_level='Explicit',confidence='High',evidence_id=eid,coder_note='Assistant contextual review, codebook v1, 2026-11-02. '+notes[sid]+' Self-description, not independently verified practice.',review_status='Reviewed'))
add(ids[0],'nordic_about','Undervisningen – undervisning på svenska med en internationellt inspirerad pedagogik, förankrad i forskning om hur elever lär sig bäst')
add(ids[1],'mag_unit','På vår resursskola är den pedagogiska miljön genomtänkt och anpassad utifrån elevernas behov. Grupperna är små, lärartätheten hög och elevhälsan förstärkt för att eleven ska ges möjlighet att utvecklas i sina studier och känna att de lyckas.','Support, inclusion, or wellbeing emphasis','Resource school / individualised support')
add(ids[2],'friskola','Södertälje friskola har språkprofil. Du märker det genom att vi har ökat ut undervisningstiden i svenska och engelska.','Language, international, or intercultural profile','Language profile: Swedish and English')
add(ids[4],'pershagen','Vi har ett stort intresse för teknik och de naturvetenskapliga ämnena och arbetar med att utveckla vår teknikprofil tillsammans med andra aktörer i kommunen.','Other stated profile','Developing technology profile')
add(ids[5],'broang_current','För att uppnå detta är vi en del av kommunens våldsförebyggande arbete ”Tåget” (eller ”MVP” som det heter för åk 7-9) som sker i samarbete med socialtjänsten.','Support, inclusion, or wellbeing emphasis','Tåget / MVP violence prevention')
add(ids[6],'farsta_about','Adolf Fredriks musikklasser årskurs 4-9 Elever i musiklass uppträder på många olika sätt och olika sammanhang, till exempel med konsert för vårdnadshavare och anhöriga. I musikundervisningen sjunger du främst i kör. Du får även spela instrument i grupp. Du har musiklektioner varje dag på schemat.','Arts and creative learning','Music / choir classes, years4–9 only')
add(ids[8],'ies','Internationella Engelska Skolan (IES) Enskede provides a unique and high-quality bilingual education, with up to 50 % of lessons taught in English.','Language, international, or intercultural profile','Bilingual Swedish/English, years4–9')
validate_records(e,c)
logs=[];reviews=[]
for r in selection:
 sid=r['school_id'];reviews.append(dict(school_id=sid,school_name=r['official_directory_name'],outcome=outcomes[sid],evidence_count=sum(x['school_id']==sid for x in e),code_count=sum(x['school_id']==sid for x in c),unit_scope=notes[sid],follow_up=notes[sid],reviewer='Assistant contextual review; not independent verification',accessed_date=D,load_state='Staged, not loaded'))
 for n in pages[sid]:
  note='Saved public page, fetched2026-11-02; precise retrieval time not retained; date is not a coding-date substitution.'
  if n=='magelungen':note+=' Requested https://magelungen.com/grundskola/alvsjo/ redirected to selected contact page; insufficient evidence there.'
  if n=='steninge':note+=' Requested /pa-skolan/valkommen-till-steningehojdens-skola.html redirected to /pa-steningehojdens-skola/ path.'
  logs.append(dict(school_id=sid,registered_url=r['registered_url'],selected_url=u[n],page_title=title(n),accessed_date=D,status=404 if n in ['pershagen_old','broang'] else 200,saved_file='sources/'+n+'.html',selection_rationale='Ascending pending official ID; official/provider descriptive unit pages.',scope=notes[sid],outcome=outcomes[sid],permissions='Public descriptive paths; saved robots inspected, no selected descriptive path excluded. Magelungen robots404 not clearance; no bypass. Terms not exhaustively reviewed; minimal quotations.',exclusions='No login/admin/applications/social/gallery/pupil-survey follow-up; incidental contact/news material not analysed or curated as evidence.',retrieval_note=note))
for n,v in [('selection.json',selection),('official_selection_metadata.json',meta),('Approach_evidence.staged.json',e),('Approach_codes.staged.json',c)]:dump(n,v)
for n,rs in [('review_log.csv',reviews),('collection_log.csv',logs)]:
 with (B/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
(B/'collection_log.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in logs))
dump('source_hashes.json',{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(S.iterdir()) if x.is_file()})
dump('staging_validation.json',dict(status='PASSED',schools=10,evidence=len(e),codes=len(c),exact_own_source_quotes=len(e),official_ids_valid=True,selection_matches_ledger=True))
(B/'decision_log.md').write_text('# Batch23 decisions\n\n'+'\n\n'.join(sid+': '+notes[sid] for sid in ids)+'\n\nCodebook v1 retained. About/pedagogy/education/profile/creative/arts/learning/values concepts in Swedish/English used for scoped official-page navigation and contextual review; not exhaustive web search. Reviewed school wording is not independently verified practice. No county scope audit inferred from outcomes.\n')
(B/'REPORT.md').write_text('# Batch23 — 2 November 2026\n\n10 outcomes: 6 schools with6 reviewed codes;1 uncertain/no firm code;3 scoped no-clear-evidence.7 evidence rows. Farsta music4–9 selected classes only; Magelungen resource-school placements; Broäng shared rector-area programme; Pershagen developing technology profile. IES about-page Karlstad copy excluded. Historical failed links preserved.\n\nStaged; load/checkpoint pending.\n')
dump('batch_status.json',dict(status='STAGED_VALIDATED_NOT_LOADED',schools=10,evidence=len(e),codes=len(c),date=D))
print(json.dumps(dict(schools=10,evidence=len(e),codes=len(c))))
