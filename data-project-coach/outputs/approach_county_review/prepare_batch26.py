"""Create Batch26 staging from the preserved Batch25 format, never execute Batch25."""
from pathlib import Path
import ast,difflib
P=Path('outputs/approach_county_review')
s=(P/'build_batch25.py').read_text()
s=s.replace('Batch25','Batch26').replace('batch25','batch26').replace('b25_','b26_').replace('after_batch24','after_batch25')
a=s.index("ids=[r['school_id']")
b=s.index('with duckdb.connect',a)
s=s[:a]+"ids=[r['school_id'] for r in selection];assert ids==['41213404','41285467','41357379','41377165','41405700','41507895','41554150','41584790','41764666','41888515']\n"+s[b:]
a=s.index('u=dict(');b=s.index('def title(',a)
s=s[:a]+'''u=dict(kallbrink='https://www.huddinge.se/kallbrinksskolan',kallbrink_about='https://www.huddinge.se/kallbrinksskolan/om-skolan',adolf='https://grundskola.stockholm/hitta-grundskola/grundskola/adolfsbergsskolan',skogs='https://www.botkyrka.se/skola-och-forskola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/skogsbacksskolan',sundby='https://www.ekero.se/forskola-skola/grundskola/skolor-i-ekero-kommun/sundby-skola-f-6',storkyrko='https://grundskola.stockholm/hitta-grundskola/grundskola/storkyrkoskolan',nobla='https://noblaskolan.se/nacka-strand/',nobla_about='https://noblaskolan.se/nacka-strand/om/grundskola/',slott='https://www.taby.se/slottsparksskolan',jarna='https://www.jarnafriskola.se/',jarna_about='https://www.jarnafriskola.se/var-skola/',langbrodal='https://grundskola.stockholm/hitta-grundskola/grundskola/langbrodalsskolan',fardala='https://www.tyreso.se/forskola--skola/skolbarn/alla-grundskolor/fardala-skola.html')
page_sets=[['kallbrink','kallbrink_about'],['adolf'],['skogs'],['sundby'],['storkyrko'],['nobla','nobla_about'],['slott'],['jarna','jarna_about'],['langbrodal'],['fardala']]
notes_list=[
'Website F–9; shared rector area not generalized. Accessibility described as a strength, but broad relational/support wording lacks a sufficiently concrete distinctive model; retained as uncertain note, no firm code.',
'Website F–6 with separate addresses by year. Reviewed descriptive page only; ordinary teams, premises and fritids do not establish an approach. No clear evidence within this scope, not evidence of absence.',
'PERMISSION BLOCKER: prior terms_review_required remains unresolved; robots is not terms clearance. General Skogsbacksskolan page already fetched, but does not mention Trampolinen. No profile transferred; no approach evidence curated or coded. Resolve terms and ID-bearing Trampolinen mapping before substantive collection resumes.',
'Website F–6; nature-adjacent location and generic leadership/accessibility are not outdoor pedagogy. Registered HTTP not separately fetched; HTTPS short path redirected to selected descriptive path. Scoped no-clear.',
'Website F–6. Generic creative/stimulating wording, cultural heritage and assemblies do not establish arts-based pedagogy. No clear evidence within descriptive-page scope.',
'Website preschool through year3; only compulsory-school F–3 page and common Noblakoden context used. Target overlap years1–3. Outdoor pedagogy explicitly stated, frequency unspecified. Promotional attainment claims excluded; no effectiveness inference.',
'Website F–3; target overlap1–3. IBIS named as preventive model. Research/evidensbaserad wording is school self-description, not verified effectiveness. University assessment collaboration not a profile.',
'Website F–9; explicit Montessori-inspired rather than certified/full Montessori. Outdoor didactics explicitly integrated into teaching. About page references 2024 anniversary, so pupil count/current implementation not independently verified.',
'Website F–6, two buildings and external PE location for4–6. Ordinary support, movement, theme weeks and nearby woods do not by themselves establish a distinctive approach. Scoped no-clear.',
'Website F–6; cooperative learning and elevhälsa i varje vrå are developing step-by-step, not verified fully implemented. Trivselledare starts year2; recurring activities two days/week. Separate municipal tal/språk learning studio not generalized. Impact assertions excluded.'
]
notes=dict(zip(ids,notes_list));outcomes=dict(zip(ids,['Uncertain evidence / requires review','No clear evidence within scoped review','Permission blocker / unresolved unit identity','No clear evidence within scoped review','No clear evidence within scoped review','Reviewed approach claim','Reviewed approach claim','Reviewed approach claim','No clear evidence within scoped review','Reviewed approach claim']))
''' +s[b:]
a=s.index("add(1,");b=s.index('validate_records(e,c)',a)
s=s[:a]+'''add(0,'kallbrink_about','Tillgängligt lärande är en av våra största styrkor och genomsyrar undervisningen, lärmiljöerna och skolans organisation.')
add(5,'nobla','Därför har vi skapat Noblakoden – ett gemensamt förhållningssätt kring lektionsstruktur, ordning, mentorsrollen och andra saker som är viktiga för en bra skolmiljö.','Support, inclusion, or wellbeing emphasis','Noblakoden structured learning environment')
add(5,'nobla_about','Språk, läsning och samtal har en självklar plats i alla ämnen, och lärandet förstärks genom rörelse och utomhuspedagogik.','Outdoor, nature, or place-based learning','Outdoor pedagogy, years1–3 overlap')
add(6,'slott','IBIS står för inkluderande beteendestöd i skolan och utvecklar vårt förebyggande arbete med trygghet och studiero.','Support, inclusion, or wellbeing emphasis','IBIS, years1–3 overlap')
add(7,'jarna_about','Vi är en Montessoriinspirerad skola, vilket innebär att vi arbetar efter Montessoripedagogikens grundläggande tankar kring barns utveckling och inlärning.','Alternative pedagogy','Montessori-inspired')
add(7,'jarna','utomhusdidaktik ingår som ett naturligt moment i undervisningen.','Outdoor, nature, or place-based learning','Outdoor didactics integrated into teaching')
add(9,'fardala','Vi befinner oss i ett utvecklingsarbete i kooperativt lärande samt elevhälsa i varje vrå som implementeras steg för steg i alla klassrum.','Other stated profile','Cooperative learning and elevhälsa i varje vrå, developing')
add(9,'fardala','Vi är en trivselskola vilket betyder att vi har utbildade trivselledare i alla årskurser från årskurs 2.','Support, inclusion, or wellbeing emphasis','Trivselledare, from year2')
''' +s[b:]
s=s.replace('Ascending pending official ID; official/provider unit description and relevant curriculum/language follow-up.','Ascending pending official ID; official/provider descriptive school pages and teaching/about follow-ups. General Skogsbacksskolan source held for identity/permission review, not coded.')
a=s.index("permissions='Robots");b=s.index(",exclusions=",a)
s=s[:a]+"permissions='Robots responses saved for eight hosts. Stockholm malformed68-byte response not affirmative clearance; Järna empty file. Skogsbacksskolan prior terms flag unresolved and page was fetched before resolving it; no additional collection or approach evidence curated for that unit. No exhaustive terms clearance asserted; no bypass.'"+s[b:]
a=s.index("retrieval_note='");b=s.index("'))",a)
s=s[:a]+"retrieval_note='Public HTML accessed 2026-11-02; precise fetch timestamps not retained. Sundby requested HTTPS short path redirected to full selected path; registered HTTP roots not separately tested. Fårdala selected official school path instead of generic municipal root. Other saved descriptive requests returned200 at selected URLs."+s[b:]
s=s.replace('Two generic provider-name mappings held uncoded pending identity clarification.','Källbrink broad evidence held uncoded; Skogsbacksskolan Trampolinen permission and unit mapping unresolved.')
s=s.replace('10 outcomes:5 reviewed-claim schools,2 uncertain identity mappings (no firm codes),3 scoped no-clear.9 evidence excerpts /7 codes. Sources accessible; Björkeby embedded video unreviewed.','10 outcomes:4 reviewed-claim schools,1 uncertain (no firm code),4 scoped no-clear,1 unresolved permission/identity blocker.8 evidence excerpts /7 codes. Page availability does not clear permissions or unit applicability.')
ast.parse(s)
assert not (P/'build_batch26.py').exists()
(P/'build_batch26.py').write_text(s)
(P/'build_batch26.diff').write_text(''.join(difflib.unified_diff([],s.splitlines(True),fromfile='/dev/null',tofile='build_batch26.py')))
print('New Batch26 builder syntax PASSED',len(s.splitlines()),'lines; not executed')
