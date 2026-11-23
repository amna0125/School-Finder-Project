"""One-time Batch24 staging; guarded against reruns."""
from pathlib import Path
import csv,json,re,html,hashlib
import duckdb
from outputs.approach_county_review.extract19 import parse
from school_pipeline.approach_migration import validate_records
P=Path('outputs/approach_county_review');B=P/'batch24_10schools_20261102';S=B/'sources';D='2026-11-02'
assert not (B/'Approach_evidence.staged.json').exists()
def dump(n,v):(B/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,default=str)+'\n')
rows=list(csv.DictReader((P/'county_progress_20261102_after_batch23.csv').open()))
selection=sorted((r for r in rows if r['review_state']=='Not yet contextually reviewed'),key=lambda r:r['school_id'])[:10]
assert selection==json.loads((P/'next_batch_after_batch23.json').read_text())
ids=[r['school_id'] for r in selection]
assert ids==['39130058','39171821','39195819','39229061','39351914','39453214','39568857','39907811','39923451','40175889']
with duckdb.connect('.state/schools.duckdb',read_only=True) as db:
 cur=db.execute('select * from schools where school_unit_code in ('+','.join('?' for _ in ids)+') order by school_unit_code',ids)
 names=[x[0] for x in cur.description];meta=[dict(zip(names,r)) for r in cur.fetchall()]
u=dict(montessori='https://www.montessoriskolan.nu',montessori_unit='https://www.montessoriskolan.nu/skolor/lunden-f-6/',montessori_pedagogy='https://www.montessoriskolan.nu/montessoripedagogik/',orby='https://grundskola.stockholm/hitta-grundskola/grundskola/orbyskolan',sandudden='https://www.ekero.se/forskola-skola/grundskola/skolor-i-ekero-kommun/sanduddens-skola-f-7',ostra='https://www.huddinge.se/ostra-grundskolan',ostra_about='https://www.huddinge.se/ostra-grundskolan/om-skolan',norrsund='https://www.norrtalje.se/info/barn-och-skola/grundskola/grundskolor/norrsundsskolan/',norrsund_about='https://www.norrtalje.se/info/barn-och-skola/grundskola/grundskolor/norrsundsskolan/var-skola/',sofieberg='https://www.tyreso.se/forskola--skola/skolbarn/alla-grundskolor/sofiebergsskolan.html',berghem='https://www.jarfalla.se/forskolaskolaochutbildning/grundskola/grundskola/jakobsberg/berghemskolan.4.5447d13a1611d09c8635f3d.html',sofielund='https://www.sollentuna.se/uweb/sofielundsskolan/om-oss/',sofielund_olweus='https://www.sollentuna.se/uweb/sofielundsskolan/sa-har-arbetar-vi/trygghet-och-studiero/vart-arbete-mot-mobbning/',kista='https://www.sverigefinskaskolanikista.se/sverigefinskaskolanikista/',kista_extern='https://www.sverigefinskaskolanikista.se/sverigefinskaskolanikista/extern/',kista_presentation='https://www.sverigefinskaskolanikista.se/sverigefinskaskolanikista/presentation.htm',soldala='https://www.sodertalje.se/skola-och-forskola/grundskola/alla-grundskolor/soldalaskolan/')
pages=dict(zip(ids,[['montessori','montessori_unit','montessori_pedagogy'],['orby'],['sandudden'],['ostra','ostra_about'],['norrsund','norrsund_about'],['sofieberg'],['berghem'],['sofielund','sofielund_olweus'],['kista','kista_extern','kista_presentation'],['soldala']]))
notes=dict(zip(ids,[
'Unresolved identity/applicability: directory Vigelsjö, official DB Montessoriskolan i Norrtälje years1–4; current provider page Lunden F–6/F–4 and5–6 at Sveagatan18. Montessori materials and working methods explicit for Lunden; no current official-ID bridge established. Provider history/pedagogy not assigned as a firm unit code. Template USA/contact junk excluded. Requires review of current unit mapping.',
'Current school page explicitly F–6 from2026/27 after7–9 move to Nya Enskede; official1–6 consistent. Programming stated as a continuous thread, with annual shared programming day in collaboration with Tekniska museet. Other stated profile, not alternative or inquiry pedagogy. No effectiveness inference.',
'Current F–7 website progressively expanding to F–9 conflicts with official1–9. Do not apply current claims to years8–9. Scoped homepage/about-content review found general teaching/support and nature access but no clear distinctive approach. Grade/status follow-up unresolved.',
'Official7–9 matches ordinary school section. Homepage/about reviewed; generic relational learning, safety and pupil participation insufficient for firm code. Same about page separately covers Östra anpassade grundskola F–9: excluded from this unit. No clear evidence in reviewed scope, not absence of approach.',
'Official7–9 matches school page; shared Älmsta rector-area leadership not a universal approach code. Homepage/our-school reviewed. General individualisation, iPads, NPF staff training and teacher professional development insufficient to establish a distinctive support/alternative profile; no clear evidence within scope.',
'F–3 website vs official1–3. Support code restricted to attached lärstudio, explicitly a central special teaching group offering support and family intervention; not every pupil. Grön Flagg and nearby nature descriptions retained as context, not automatically an outdoor approach code. No quality/staffing verification.',
'F–6 vs official1–6. Homepage and embedded grundskola/förskoleklass/fritids content reviewed. Weekly forest and Bornholm model descriptions refer to preschool class only; excluded from compulsory years1–6 approach coding. Generic inclusion/critical thinking insufficient. Temporary Mälarvägen2 premises; projected new building HT2028, not verified future event. Conflicting website headcounts not used as statistics.',
'F–9 vs official1–9. School-specific navigation hosts explicit Olweus programme description with coordinated routines and pupil/staff/guardian participation; municipal-wide programme, not unique to this school. STL abbreviation/visitors alone not sufficient alternative/inquiry category. School wording, no independently verified impact.',
'Registered HTTPS-equivalent request redirects to /sverigefinskaskolanikista/ with empty-title meta-refresh to extern; extern endpoint redirects to trailing slash and displays template placeholder. Presentation link404. No usable substantive profile evidence; inaccessible/failed substantive source, not no approach. Do not infer Swedish/Finnish provision from school name. Official1–5 scope uncorroborated by usable current content.',
'F–9 website vs official1–9. Explicit El Sistema opportunity for F–2 only (within official compulsory scope years1–2); no universal music profile. Generic multimodal/creative wording not separately coded. Outdoor opportunities in woodland not evidence of implemented outdoor approach. Named staff/social content excluded.'
]))
outcomes={sid:('Uncertain evidence — no firm code' if i==0 else 'Inaccessible substantive source — requires review' if i==8 else 'Reviewed approach claims' if i in [1,5,7,9] else 'No clear evidence within scoped review') for i,sid in enumerate(ids)}
def title(n):
 m=re.search(r'<title[^>]*>(.*?)</title>',(S/(n+'.html')).read_text(),re.S|re.I)
 return html.unescape(re.sub(r'\s+',' ',m[1])).strip() if m else ''
e=[];c=[]
def add(i,n,quote,cat=None,sub=''):
 sid=ids[i];assert quote in parse(S/(n+'.html'))[0],(n,quote)
 eid=f'ae_b24_{sid}_01'
 e.append(dict(evidence_id=eid,school_id=sid,source_url=u[n],page_title=title(n),accessed_date=D,quoted_text=quote,evidence_type='School webpage',interpretation_note=notes[sid]))
 if cat:c.append(dict(code_id=f'ac_b24_{sid}_01',school_id=sid,category=cat,subcategory=sub,coding_level='Explicit',confidence='High',evidence_id=eid,coder_note='Assistant contextual review, codebook v1, 2026-11-02. '+notes[sid]+' Self-description, not independently verified practice.',review_status='Reviewed'))
add(0,'montessori_unit','För att möta eleven i sin kunskapsutveckling har vi många olika arbetsmaterial i klassrummet: konkret montessorimaterial, lärplattor (ikt), läroböcker, biblioteksböcker, material från naturen.')
add(1,'orby','Vi har programmering som en röd tråd och ditt barn får lära sig programmera på ett lustfyllt sätt. Varje läsår genomför vi en gemensam programmeringsdag i samarbete med Tekniska museet.','Other stated profile','Programming emphasis, F–6')
add(5,'sofieberg','Till skolan hör även en lärstudio (central särskild undervisningsgrupp) som erbjuder stödinsatser och familjebehandling.','Support, inclusion, or wellbeing emphasis','Attached lärstudio / special teaching group only')
add(7,'sofielund_olweus','Alla kommunala skolor i Sollentuna arbetar utifrån Olweusprogrammet. Det är en serie samordnade, forskningsbaserade åtgärder som går ut på att skapa en skolmiljö där eleverna kan lära, trivas och känna sig trygga.','Support, inclusion, or wellbeing emphasis','Olweus anti-bullying programme, municipal-wide')
add(9,'soldala','Tack vare detta samarbete får elever i årskurs F–2 fördjupa sig i musik och lära sig spela olika instrument tillsammans – en upplevelse som stärker både självkänsla och gemenskap.','Arts and creative learning','El Sistema opportunity, F–2 only')
validate_records(e,c)
logs=[];reviews=[]
for r in selection:
 sid=r['school_id'];reviews.append(dict(school_id=sid,school_name=r['official_directory_name'],outcome=outcomes[sid],evidence_count=sum(x['school_id']==sid for x in e),code_count=sum(x['school_id']==sid for x in c),unit_scope=notes[sid],follow_up=notes[sid],reviewer='Assistant contextual review; not independent verification',accessed_date=D,load_state='Staged, not loaded'))
 for n in pages[sid]:
  provenance='Saved public source, accessed2026-11-02; precise fetch times not retained. Selected current official/provider page discovered via search/navigation; registered HTTP URL not separately requested and no unobserved redirect asserted.'
  if n=='kista':provenance+=' HTTPS root requested; redirected to /sverigefinskaskolanikista/;200 meta-refresh to extern, empty title.'
  if n=='kista_extern':provenance+=' Requested without trailing slash; redirected to trailing slash;200 placeholder.'
  if n=='kista_presentation':provenance+='404 from linked Presentation page retained.'
  logs.append(dict(school_id=sid,registered_url=r['registered_url'],selected_url=u[n],page_title=title(n),accessed_date=D,status=404 if n=='kista_presentation' else 200,saved_file='sources/'+n+'.html',selection_rationale='Ascending pending official ID; scoped official/provider about/pedagogy/teaching/profile review.',scope=notes[sid],outcome=outcomes[sid],permissions='Saved robots inspected after initial descriptive fetches; no selected path disallowed. Kista robots404 is not affirmative permission. No bypass; terms not exhaustively reviewed; minimal quotations.',exclusions='No login/admin/application/social/gallery or pupil-survey follow-up; incidental named staff not curated as evidence.',retrieval_note=provenance))
for n,v in [('selection.json',selection),('official_selection_metadata.json',meta),('Approach_evidence.staged.json',e),('Approach_codes.staged.json',c)]:dump(n,v)
for n,rs in [('review_log.csv',reviews),('collection_log.csv',logs)]:
 with (B/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rs[0]);w.writeheader();w.writerows(rs)
(B/'collection_log.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in logs))
dump('source_hashes.json',{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(S.iterdir()) if x.is_file()})
dump('staging_validation.json',dict(status='PASSED',schools=10,evidence=len(e),codes=len(c),official_ids_valid=True,selection_matches_ledger=True))
(B/'decision_log.md').write_text('# Batch24 decisions\n\n'+'\n\n'.join(sid+': '+notes[sid] for sid in ids)+'\n\nCodebook v1 unchanged. Swedish/English about, pedagogy, education, profile, creative, arts, learning and values concepts used for scoped navigation and review; not exhaustive search. No county scope totals inferred.\n')
(B/'REPORT.md').write_text('# Batch24 — 2 November 2026\n\n10 outcomes:4 reviewed schools/4 codes;1 uncertain unit mapping;4 scoped no-clear;1 inaccessible substantive source.5 evidence rows. Montessori identity unresolved; Sandudden current F–7 vs official1–9. Östra separate anpassad content excluded. Sofieberg learning studio only; Soldala El Sistema F–2 only; Sofielund municipal Olweus programme; Örby programming emphasis.\n\nStaged; load/checkpoint pending.\n')
dump('batch_status.json',dict(status='STAGED_VALIDATED_NOT_LOADED',schools=10,evidence=len(e),codes=len(c),date=D))
print(json.dumps(dict(schools=10,evidence=len(e),codes=len(c))))
