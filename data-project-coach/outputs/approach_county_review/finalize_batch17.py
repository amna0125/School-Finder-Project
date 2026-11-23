"""One-time Batch17 audit builder; no network or database writes."""
from pathlib import Path
import csv, hashlib, html, json, re
from school_pipeline.approach_migration import validate_records
P=Path('outputs/approach_county_review'); B=P/'batch17_10schools_20261030'; S=B/'sources'; D='2026-10-30'
assert not (B/'Approach_evidence.staged.json').exists()
def text(n):
 s=(S/(n+'.html')).read_text();s=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S);return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def title(n):
 return html.unescape(re.search(r'<title[^>]*>(.*?)</title>',(S/(n+'.html')).read_text(),re.S|re.I)[1]).strip()
u={
'gondolen':'https://www.esgondolen.se/','gondolen_about':'https://www.esgondolen.se/om-oss','gondolen_bilingual':'https://www.esgondolen.se/tv%C3%A5spr%C3%A5kig-utbildning',
'saga':'https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/sagaskolan/pa-sagaskolan/valkommen-till-sagaskolan.html','saga_methods':'https://www.sigtuna.se/utbildning-och-barnomsorg/grundskola/grundskolor/sagaskolan/arbetssatt-och-kvalitetsarbete.html',
'jensen':'https://www.jensengrundskola.se/tungelsta','jensen_about':'https://www.jensengrundskola.se/vara-skolor/tungelsta/om-skolan','jensen_health':'https://www.jensengrundskola.se/att-ga-pa-jensen/halsofokus',
'aby':'https://abyskolan.haninge.se/var-skola/','aby_methods':'https://abyskolan.haninge.se/sa-har-jobbar-vi/',
'riala':'https://www.norrtalje.se/info/barn-och-skola/grundskola/grundskolor/riala-skola/','riala_about':'https://www.norrtalje.se/info/barn-och-skola/grundskola/grundskolor/riala-skola/var-skola/',
'vasby':'https://www.upplandsvasby.se/skola/vasby-skola','vasby_about':'https://www.upplandsvasby.se/skola/vasby-skola/om-skolan',
'nyboda':'https://www.tyreso.se/forskola--skola/skolbarn/alla-grundskolor/nyboda-skola.html','nyboda_profile':'https://www.tyreso.se/forskola--skola/skolbarn/alla-grundskolor/nyboda-skola/profilklass---idrott.html',
'maria':'https://mariaskolan.nu/','maria_pedagogy':'https://mariaskolan.nu/waldorfpedagogik/',
'urfjall':'https://urfjall.se/','urfjall_school':'https://urfjall.se/skolan/',
'margretelund':'https://www.osteraker.se/subsitegrundskolor/margretelundsskolan.4.367d658917909e8fc2b8d17.html','margretelund_about':'https://www.osteraker.se/subsitegrundskolor/margretelundsskolan/omskolan.4.367d658917909e8fc2b8d33.html','margretelund_reading':'https://www.osteraker.se/subsitegrundskolor/margretelundsskolan/omskolan/lasprojekt.4.77723db318514fad1179da7.html','margretelund_safety':'https://www.osteraker.se/subsitegrundskolor/margretelundsskolan/omskolan/trygghetsteametjunior.4.44fe6fa019e40e754cde579.html'}
e=[];c=[]
def add(sid,n,q,note,cat=None,sub=''):
 assert q in text(n),(n,q)
 eid=f'ae_b17_{sid}_{sum(x["school_id"]==sid for x in e)+1:02d}'
 e.append(dict(evidence_id=eid,school_id=sid,source_url=u[n],page_title=title(n),accessed_date=D,quoted_text=q,evidence_type='Official school/provider public description',interpretation_note=note))
 if cat:c.append(dict(code_id=f'ac_b17_{sid}_{sum(x["school_id"]==sid for x in c)+1:02d}',school_id=sid,category=cat,subcategory=sub,coding_level='Explicit',confidence='High',evidence_id=eid,coder_note='Assistant contextual review, codebook v1, 2026-10-30. '+note+' Public claim, not independently verified practice.',review_status='Reviewed'))
add('29796042','gondolen_about','tvåspråkig', 'Website states bilingual F–9 provision. Current schools table names this ID Engelska skolan Gondolen; ledger uses ESF Skarpnäck AB. Registered domain and Skarpnäck location match; retain historical name discrepancy. Expanded timetable and Cambridge opportunities are claims, not outcomes.','Language, international, or intercultural profile','Swedish–English bilingual')
add('29998540','saga','Vi ligger centralt i Valsta, med närhet till fina naturområden som vi regelbundet använder i både skola och fritids.','Unclear/Low: recurring nature use stated but no concrete curricular or structured outdoor method. School versus fritids scope not separated. No firm code; requires review.')
add('30255409','jensen','Skolan har också en tydlig hälsoprofil.','Local F–9 health-profile self-label. Provider health page supplies context, not independently verified local routines.','Support, inclusion, or wellbeing emphasis','Health profile')
add('30270791','aby_methods','Att eleverna mår bra ser vi som en förutsättning för goda prestationer och ett gott lärande, vilket är en av anledningarna till varför elever erbjuds frukost.','Page updated 17 April 2023; breakfast offer alone and generic community language do not establish a distinctive approach. No firm code; scoped no-clear-evidence outcome, not absence of an approach.')
add('30490775','riala','Riala skola','Scoped review of school and about pages: nature as opportunity, subject provision and ordinary pupil health duties insufficient. No firm code. Website F–6 versus official grades1–5 retained as unresolved discrepancy.')
add('31018677','vasby_about','På Väsby skola har vi i första hand fokuserat på social hållbarhet.','Explicit local social-sustainability focus. Preceding award criteria are criteria, not separately demonstrated practices; award claim not independently verified.','Other stated profile','Social sustainability')
add('31281674','nyboda_profile','På Nyboda skola finns idrottsprofil från årskurs 7 till 9.','Profile classes7–9 only, not all pupils. Alternating three/five sports lessons stated. Site ordinary7–9 versus official4–9 unresolved; co-located adapted unit excluded.','Other stated profile','Sports profile, years7–9 profile classes')
add('31528772','maria','Mariaskolan är en liten trivsam, icke vinstdrivande Waldorfskola centralt i Järna, med gångavstånd till pendeltåg och busshållplatser.','Named Waldorf school F–9. Homepage retains stale lgr11 wording; no inference of current curriculum compliance. Provider pedagogy F–12 discussion not unit grades.','Alternative pedagogy','Waldorf/Steiner')
add('31528772','maria','Teoretiska, praktiska och konstnärliga ämnen integreras för att hela människan skall ha möjlighet att vara aktiv i inlärnings-processen.','Explicit integrated theoretical/practical/artistic teaching self-description. Retain homepage stale curriculum caveat.','Arts and creative learning','Arts integration')
add('31608087','urfjall_school','Montessoripedagogikens värdegrund är en medveten del av arbetet på skolan. I förskoleklass arbetar vår erfarna montessoripedagog med montessoripedagogikens material och arbetssätt.','F–3 school: values school-wide; concrete Montessori materials/methods specifically preschool class. Do not infer methods in every grade or transfer preschool provision.','Alternative pedagogy','Montessori values; materials/methods in preschool class')
add('31758556','margretelund_safety','Trygghetsteamet junior består av elever på skolan som är ute på raster för att hålla lite extra koll så att alla har det bra och att alla som vill har någon att leka med.','Named pupil peer-support routine; scheduled team meetings described. Page updated25 September2026. No named pupils or images used.','Support, inclusion, or wellbeing emphasis','Trygghetsteamet junior peer support')
add('31758556','margretelund_reading','Margretelundsskolans läsprojekt','Named sustained reading project across classrooms and fritids plus library and staff development. Page updated23 April2024, persistence not independently verified. Not inquiry-based merely because called a project.','Other stated profile','På väg mot 50 000 reading project')
# Replace overly short anchors with faithful contextual sentences when available.
for row,n,start,end in [(e[0],'gondolen_about','Hösten 2025',None),(e[4],'riala','Riala skola är',None)]:
 t=text(n);i=t.find(start)
 if i>=0:
  stop=t.find('.',i)
  if stop>=0:row['quoted_text']=t[i:stop+1]
validate_records(e,c)
selection=json.loads((P/'next_batch_after_batch16.json').read_text());assert len(selection)==10
ids=[r['school_id'] for r in selection];assert ids==sorted(ids)
notes={
'29796042':('Reviewed claim','F–9; official1–9; Skarpnäck.','Current official table name Gondolen vs historical ledger ESF Skarpnäck AB; legal/name lineage not fully reconstructed; robots404 HTML, permission uncertainty retained.'),
'29998540':('Uncertain evidence','Valsta F–6; official1–6.','Regular nature use lacks concrete method; requires review, no firm code. Municipal methods page is generic links.'),
'30255409':('Reviewed claim','Local Tungelsta F–9; official1–9.','Health focus explicit locally; provider routines not independently verified locally. Other schools spetsutbildning excluded.'),
'30270791':('Scoped no clear evidence','Västerhaninge F–6; official1–6.','About and methods reviewed. Breakfast page2023; community wording generic; do not infer no approach.'),
'30490775':('Scoped no clear evidence','Riala skolväg6; websiteF–6 vs official1–5.','Grade discrepancy requires follow-up. Nature opportunity not outdoor method; practical arts at Länna not an arts profile.'),
'31018677':('Reviewed claim','Väsby school F–9; official1–9.','Social sustainability self-description, not verified award or implementation; criteria not additional practice evidence.'),
'31281674':('Reviewed claim','Sports classes7–9 only; official unit4–9.','Grade discrepancy requires follow-up; adapted school separate; profile selection/test requirements not effectiveness evidence.'),
'31528772':('Reviewed claim','Mariaskolan Järna F–9; official1–9.','Stale lgr11 wording; general Waldorf F–12 passage not unit scope; events/gallery/preschool excluded.'),
'31608087':('Reviewed claim','Urfjäll Kungsängen F–3; official1–3.','Successful access supersedes older inaccessible status. Montessori values school-wide, materials specifically F-class. Preschool excluded.'),
'31758556':('Reviewed claim','Margretelund F–6; official1–6.','Reading page2024 remains dated claim; junior safety team page2026. Ordinary library/support provision not independently added as profile.')}
groups=[['gondolen','gondolen_about','gondolen_bilingual'],['saga','saga_methods'],['jensen','jensen_about','jensen_health'],['aby','aby_methods'],['riala','riala_about'],['vasby','vasby_about'],['nyboda','nyboda_profile'],['maria','maria_pedagogy'],['urfjall','urfjall_school'],['margretelund','margretelund_about','margretelund_reading','margretelund_safety']]
perm='Public clean school/provider paths only; saved robots reviewed. JENSEN full2141-byte policy does not disallow selected paths. Gondolen robots404 HTML is unresolved policy uncertainty, not blanket permission. Other saved policies do not visibly block selected paths; terms not comprehensively audited. No login/application/admin/social/gallery collection, no controls bypassed. Swedish/English concepts: om skolan/about, pedagogik/pedagogy, utbildning/education, profil/profile, skapande/creative, konst/arts, lärande/learning, värdegrund/values; scoped navigation, not exhaustive site search.'
for name,data in [('Approach_evidence.staged.json',e),('Approach_codes.staged.json',c),('selection.json',selection)]: (B/name).write_text(json.dumps(data,ensure_ascii=False,indent=2))
fields=['school_id','official_directory_name','outcome','evidence_rows','code_rows','unit_scope','followup_note','reviewer','review_date','load_status']
with (B/'review_log.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in selection:
  sid=r['school_id'];out,scope,note=notes[sid];w.writerow(dict(school_id=sid,official_directory_name=r['official_directory_name'],outcome=out,evidence_rows=sum(x['school_id']==sid for x in e),code_rows=sum(x['school_id']==sid for x in c),unit_scope=scope,followup_note=note,reviewer='Assistant contextual review; claims not independently verified',review_date=D,load_status='Staged; not loaded'))
with (B/'collection_log.jsonl').open('w') as f:
 for r,ns in zip(selection,groups):
  sid=r['school_id'];f.write(json.dumps(dict(school_id=sid,registered_url=r['registered_url'],selection_rationale='Next ten without documented contextual review in ascending official ID; county inclusion not dashboard selection',accessed_date=D,pages=[dict(source_url=u[n],page_title=title(n),saved_file=n+'.html',http_status=200) for n in ns],outcome=notes[sid][0],scope=notes[sid][1],limitations=notes[sid][2],permission_and_exclusions=perm,redirect_notes='Sagaskolan pa-skolan to pa-sagaskolan; Urfjall ?page_id=13 to /skolan/; broad municipality registered links replaced by named school pages'),ensure_ascii=False)+'\n')
manifest=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(S.iterdir()) if f.is_file()];(B/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
(B/'decision_log.md').write_text('# Batch17 contextual decisions\n\nExisting codebook v1 unchanged. Assistant review on2026-10-30; public claims not verified practice.\n\n'+'\n'.join('- '+sid+': '+str(notes[sid]) for sid in ids)+'\n\n'+perm+'\n\nQuotations normalized for HTML tags/entities and whitespace only. Access date confirmed by collection history and current UTC clock, not inferred from staging or directory dates. Raw HTML retained; minimal quotations published.\n')
(B/'validation.json').write_text(json.dumps(dict(status='PASSED_ARTIFACT_VALIDATION',schools=10,evidence_rows=len(e),code_rows=len(c),quote_substrings_checked=all(x['quoted_text'] in text(next(n for n in u if u[n]==x['source_url'])) for x in e),source_access_date=D),indent=2))
(B/'batch_status.json').write_text(json.dumps(dict(status='STAGED_NOT_LOADED',schools=10),indent=2))
(B/'REPORT.md').write_text('# Batch17 contextual review\n\n10 outcomes: seven reviewed-claim schools, Sagaskolan uncertain, Åbyskolan and Riala scoped no-clear-evidence. '+str(len(e))+' evidence and '+str(len(c))+' codes staged. See review log for unresolved scope, age and permissions limitations. No claim of verified practice or all-county completion. Load/checkpoint status separate.\n')
print('STAGED',len(e),len(c))
