"""Stage Batch29 without database mutation or county checkpoint updates."""
import csv, hashlib, json, re
from pathlib import Path
from html import unescape
import duckdb
from outputs.approach_county_review.extract19 import parse
from school_pipeline.approach_migration import validate_records
P=Path('outputs/approach_county_review/batch29_10schools_20261102')
DATE='2026-11-02'
def save(name,obj):
    p=P/name
    assert not p.exists(),str(p)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
selection=json.loads((P/'selection.json').read_text())
ids=[x['school_id'] for x in selection]
assert len(ids)==len(set(ids))==10 and ids==sorted(ids)
# Requested URLs and redirects are taken from recorded fetch results, not inferred timestamps.
S={
'marie':('43403496',selection[0]['registered_url'],selection[0]['registered_url']),
'enback':('43632318',selection[1]['registered_url'],selection[1]['registered_url']),
'lillapark':('43802065','https://www.lillaparkskolan.se/','https://lillaparkskolan.se/'),
'lillapark_about':('43802065','https://lillaparkskolan.se/om-skolan/','https://lillaparkskolan.se/om-skolan/'),
'fredsborg':('43869172','https://www.fredsborgskolan.se/','https://www.fredsborgskolan.se/'),
'fredsborg_unit':('43869172','https://www.fredsborgskolan.se/fredsborgskolan-f-6/','https://www.fredsborgskolan.se/fredsborgskolan-f-6/'),
'fredsborg_profile':('43869172','https://www.fredsborgskolan.se/profiler/halsa-rorelse-f-6/','https://www.fredsborgskolan.se/profiler/halsa-rorelse-f-6/'),
'ellagard':('44002887','https://www.taby.se/ellagardsskolan','https://www.taby.se/ellagardsskolan'),
'hoglunda':('44031601','https://hoglundaskolan.haninge.se/','https://hoglundaskolan.haninge.se/'),
'hoglunda_about':('44031601','https://hoglundaskolan.haninge.se/var-skola/om-skolan/','https://hoglundaskolan.haninge.se/var-skola/om-skolan/'),
'hoglunda_work':('44031601','https://hoglundaskolan.haninge.se/sa-har-jobbar-vi/','https://hoglundaskolan.haninge.se/sa-har-jobbar-vi/'),
'sundby':('44046131',selection[6]['registered_url'],selection[6]['registered_url']),
'boo_registered':('44175786','http://www.boogard.nacka.se','https://www.nacka.se/valfard-skola/boo-gard/'),
'boo_method':('44175786','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/var-verksamhet/','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/var-verksamhet/'),
'boo_international':('44175786','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/samarbeten/','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/samarbeten/'),
'boo_nta':('44175786','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/var-verksamhet/nta-och-peak/','https://www.nacka.se/valfard-skola/boo-gard/om-boo-gards-skola/var-verksamhet/nta-och-peak/'),
'grimsta':('44227469','https://www.upplandsvasby.se/grimstaskolan','https://www.upplandsvasby.se/grimstaskolan'),
'grimsta_about':('44227469','https://www.upplandsvasby.se/skola/grimstaskolan/om-skolan','https://www.upplandsvasby.se/skola/grimstaskolan/om-skolan'),
'idun':('44373961','https://www.idunskolan.se/','https://idunskolan.se/'),
'idun_today':('44373961','https://idunskolan.se/om/idunskolanidag/','https://idunskolan.se/om/idunskolanidag/'),
'idun_method':('44373961','https://idunskolan.se/om/waldorfpedagogik/','https://idunskolan.se/om/waldorfpedagogik/')}
texts={};logs=[]
for name,(sid,requested,final) in S.items():
    path=P/'sources'/(name+'.html')
    raw=path.read_text();text,_=parse(path);texts[name]=text
    title=unescape(re.search(r'<title[^>]*>(.*?)</title>',raw,re.S|re.I).group(1)).strip()
    logs.append(dict(school_id=sid,registered_url=next(x['registered_url'] for x in selection if x['school_id']==sid),requested_url=requested,final_url=final,page_title=title,accessed_date=DATE,http_status=200,source_file='sources/'+name+'.html',review_scope='School about/profile/learning environment description; relevant approach sections, not exhaustive site review',selection_rationale='Official ID order among pending schools, excluding staged Batches27–28; official municipal or school/provider website',permissions='Public pages only. Robots reviewed; no exhaustive terms clearance claimed. Stockholm robots malformed, not affirmative clearance. No access-control bypass.',exclusions='Navigation, jobs, social/gallery/login/applications, named individuals, generic results/policy wording, ordinary subjects and isolated activities excluded as approach evidence.'))
E=[];C=[]
def ev(name,quote,note):
    sid,_,url=S[name];assert quote in texts[name],(name,quote)
    eid=f'ae_b29_{sid}_{1+sum(x["school_id"]==sid for x in E):02d}'
    E.append(dict(evidence_id=eid,school_id=sid,source_url=url,page_title=next(x['page_title'] for x in logs if x['source_file']=='sources/'+name+'.html'),accessed_date=DATE,quoted_text=quote,evidence_type='School webpage',interpretation_note=note))
    return eid
def code(eid,category,subcategory,level,note):
    sid=next(x['school_id'] for x in E if x['evidence_id']==eid)
    C.append(dict(code_id=f'ac_b29_{sid}_{1+sum(x["school_id"]==sid for x in C):02d}',school_id=sid,category=category,subcategory=subcategory,coding_level=level,confidence={'Explicit':'High','Supported':'Medium'}[level],evidence_id=eid,coder_note='Assistant contextual review, not human review or independently verified practice. '+note,review_status='Reviewed'))
a=ev('enback','På Enbacksskolan har vi en gemensam struktur på undervisningen och ett arbetssätt som utvecklar ditt barns språk. Med visuellt stöd, en tydlig pedagogik och digitala hjälpmedel, får ditt barn hjälp med inlärningen.','School F–9: concrete teaching-accessibility descriptions; jointly supports inclusion emphasis rather than a language/international profile. No arts code from listed Kulturskolan/El Sistema cooperation.')
b=ev('enback','På låg- och mellanstadiet arbetar vi enligt 3-lärarsystem samt barnskötare och lärare i fritidshem som samverkar i klasserna.','Lower/middle years only. Max48 per year split into two groups is not a verified class size; do not substitute for pupils per teacher.')
code(a,'Support, inclusion, or wellbeing emphasis','Structured, accessible teaching and multi-teacher support','Supported','F–9 teaching structure; three-teacher component lower/middle years only. Supplemental evidence '+b+'.')
ev('lillapark_about','Från och med höstterminen 2026 utvecklas skolan till en renodlad lågstadieskola med klasser från förskoleklass till årskurs 3.','Current website scope F–3 from autumn2026 differs from official snapshot. Reconcile current unit/year coverage; do not transfer historical Assyrisk/Syriansk profile, described as past provision before the 2020 change.')
ev('lillapark_about','Från våren 2024 arbetar vi med Trivselledar-programmet ( trivselledare.se ) för att erbjuda alla elever fin gemenskap och rörelsepauser i klassrummet, meningsfulla raster och ett aktivt och utvecklande fritids.','Uncertain current applicability through 2026 grade transition; no firm code. Literacy/mathematics main-focus statement alone not sufficient substantive reading pedagogy.')
ev('fredsborg_profile','Genom vår profil Hälsa & Rörelse arbetar vi kontinuerligt med fysisk aktivitet och rörelse i olika former samt genom vår värdegrund för att bibehålla den goda kulturen på skolan.','Explicit self-described F–6 health/movement profile with active breaks and extra sport/outdoor activities. Uncoded pending selected official ID (snapshot years1–9) reconciliation against separately named current F–6 and 7–9 units. 2021 PEP certification is a dated school claim, not current independent certification. Outdoor-pedagogy aspiration not separately promoted.')
a=ev('ellagard','Eleverna får undervisning i välbefinnande, där de lär sig förstå sina styrkor, hantera känslor och bygga bra relationer.','F–6 school about page, dedicated wellbeing instruction with specific content rather than statutory safety text. Generic motivational effects not verified. Events/musicals do not establish arts integration.')
code(a,'Support, inclusion, or wellbeing emphasis','Wellbeing teaching','Explicit','Applies to school F–6 as described; no frequency or independently verified outcomes claimed.')
ev('boo_nta','Vi arbetar med NTA i åk 1-6.','Explicit program adoption limited to years1–6. Reviewed page does not describe an inquiry process sufficiently to make a firm inquiry-based code solely from NTA name. Follow up pedagogy/process if needed.')
ev('boo_nta','Vi arbetar också med PEAK som är en metod och arbetsredskap för hur vi kan utbilda våra elever att lära sig att arbeta medvetet med att spara energi.','Unclear/Low for category mapping: sustainability/energy method stated, but no clear outdoor/place-based teaching or sustained inquiry process. Do not infer from annual Earth Hour activity. International page mainly visitor/staff exchanges, no firm international-profile code; year9 exchange news not generalized.')
a=ev('idun_today','Idunskolan är en waldorfskola (FK- 9).','Current school self-description F–9, backed by linked substantive pedagogy page; not inferred from name. Official snapshot years1–9; preschool class is website scope. Utefritids not generalized to compulsory-school outdoor pedagogy.')
code(a,'Alternative pedagogy','Waldorf/Steiner','Explicit','Current F–9 self-description and linked pedagogy. No claim of fidelity/effectiveness.')
a=ev('idun_method','Vi arbetar med tre kunskapsfält: teori, hantverk och konst, där “konst” inte enbart är ett ämne utan ett förhållningssätt som genomsyrar alla ämnen.','Explicit cross-subject arts integration in current school-linked Waldorf pedagogy description, not an ordinary subject list. Period teaching also described but no separate inquiry code inferred.')
code(a,'Arts and creative learning','Arts integration','Explicit','Linked current F–9 Waldorf school page establishes unit applicability. Quotation is school wording, not verified teaching practice.')
D=[
('43403496','scoped_no_clear_evidence','Website 4–9; general lesson structure, varied teaching, attendance/results follow-up and safety. No distinctive approach established within single official description.','Clear within reviewed school description','None beyond normal scoped-review limits.'),
('43632318','reviewed_claims','Structured accessible teaching supported by multiple concrete descriptions; no arts code from isolated partnership list.','Clear with component year limits','Three-teacher component lower/middle years only; not class-size data. Stockholm malformed robots caveat retained.'),
('43802065','uncertain_evidence','F–3 autumn2026 transition; literacy emphasis and named wellbeing program recorded without firm codes.','Requires reconciliation','Official snapshot/current grades differ; confirm current applicability through transition. Historical Assyrisk/Syriansk profile excluded.'),
('43869172','uncertain_evidence','Explicit F–6 health/movement profile, but selected official ID snapshot years1–9 vs separate named current units.','Requires reconciliation','Resolve unit identity/current grade mapping before firm codes; do not generalize F–6 profile across high school.'),
('44002887','reviewed_claims','Explicit wellbeing teaching; no arts code from events.','Clear within reviewed school description','F–6; no frequency/effectiveness assertion.'),
('44031601','scoped_no_clear_evidence','School-specific about/work pages: generic adaptation, cooperation, safety and results goals. No distinctive approach established.','Clear within reviewed school description','Registered URL generic municipality listing; selected matching named school subdomain. Work-page merit-value goal may be inherited wording: not current outcome or approach evidence; unrelated municipal news excluded.'),
('44046131','scoped_no_clear_evidence','F–9 official description: general safety, best-break activity, green spaces, ordinary support facilities. No distinctive approach established.','Clear within reviewed school description','2024–2025 facilities section is dated; no outdoor/arts profile or support-group generalization. Stockholm robots caveat retained.'),
('44175786','uncertain_evidence','NTA years1–6 and PEAK energy method stated; category/process evidence insufficient for firm codes.','Clear for NTA years1–6; other components limited or unspecified','Follow up concrete NTA inquiry process if needed; visitor/staff exchanges do not establish whole-school international profile.'),
('44227469','scoped_no_clear_evidence','Current municipality site 6–9; generic aims, rules and safety. No distinctive approach established.','Clear within reviewed school description','Official directory Grimstaskolan vs DB Grimsta skola retained; same registered municipality route. Shared rules with adapted school not transferred as profile.'),
('44373961','reviewed_claims','Current F–9 Waldorf self-description and concrete cross-subject arts integration.','Clear within reviewed school description','Utefritids is not school-wide outdoor pedagogy. Period teaching not automatically inquiry learning.')]
R=[dict(school_id=sid,school_name=next(x['official_directory_name'] for x in selection if x['school_id']==sid),outcome=out,reviewer='Assistant contextual review',review_date=DATE,decision=decision,scope_status=scope,follow_up=follow,reviewed_sources=';'.join(x['source_file'] for x in logs if x['school_id']==sid)) for sid,out,decision,scope,follow in D]
validate_records(E,C)
assert {x['school_id'] for x in R}==set(ids)
save('Approach_evidence.staged.json',E);save('Approach_codes.staged.json',C)
save('review_log.json',R);save('collection_log.json',logs)
with (P/'collection_log.jsonl').open('x') as f:
    for row in logs:f.write(json.dumps(row,ensure_ascii=False)+'\n')
for name,rows in [('review_log.csv',R),('collection_log.csv',logs)]:
    with (P/name).open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
con=duckdb.connect('.state/schools.duckdb',read_only=True)
cur=con.execute('select * from schools where school_unit_code in (select unnest(?)) order by school_unit_code',[ids]);cols=[x[0] for x in cur.description];metadata=[dict(zip(cols,r)) for r in cur.fetchall()];assert len(metadata)==10
save('official_selection_metadata.json',metadata);con.close()
hashes=[dict(source_file=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((P/'sources').iterdir()) if p.is_file()]
save('source_hashes.json',hashes)
save('staging_validation.json',dict(schema_valid=True,selected_schools=10,evidence=len(E),codes=len(C),quote_checks=len(E),source_files=len(hashes),database_loaded=False,county_checkpointed=False))
old=json.loads((P/'batch_status.json').read_text());save('batch_status.before_staging.json',old)
new={**old,'status':'STAGED_VALIDATED_NOT_LOADED','database_loaded':False,'county_checkpointed':False,'evidence_records':len(E),'code_records':len(C),'outcomes':{k:sum(x['outcome']==k for x in R) for k in sorted({x['outcome'] for x in R})}}
(P/'batch_status.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
report='# Batch29 — structured staging only\n\nTen selected official IDs, no replacements. '+str(len(E))+' evidence records; '+str(len(C))+' codes. Three reviewed-claim schools, three uncertain schools, four scoped no-clear results. No database append/replay or county checkpoint performed. Batch30 not started.\n\n'
report+='\n'.join('- '+r['school_id']+' '+r['school_name']+': '+r['outcome']+'. '+r['decision']+' Scope: '+r['scope_status']+'. Follow-up: '+r['follow_up'] for r in R)
report+='\n\n## Collection and interpretation limits\nAccess date 2026-11-02 from actual source collection; no invented precise request timestamps. All 21 saved school pages HTTP200. Registered vs requested/final URLs retained. Generic Haninge directory replaced with matching official named school subdomain; full official-ID/address reconciliation is not claimed. Robots files saved and hashed; Stockholm malformed robots not affirmative permission. Fredsborg crawl-delay10 observed between requests. No exhaustive terms clearance asserted. No access restrictions bypassed. Scoped review is not exhaustive absence of a profile. School claims not independently verified practice.\n\nScope statuses are local review notes, not a retrospective all-checked-school scope audit. The user’s historical clear-vs-unclear scope question remains unanswered pending a defined cross-batch audit; approach outcome totals are not scope totals.\n\n## Storage boundary\nBatches1–26 last durable loaded/checkpointed history; Batches27–29 structured staging only. No county total updated here. Pipeline code unchanged; no dlt/Prefect load run or test-suite success claimed. Existing source bytes and prior reviews preserved.\n'
(P/'REPORT.md').write_text(report)
(P/'decision_log.md').write_text('# Batch29 decisions\n\n'+report+'\nCodebook compatibility: one code per school/category/subcategory with supplemental evidence IDs in notes, following current validator rather than obsolete duplicate-row wording in draft v1. Reviewed means assistant contextual review only. Explicit/High requires substantive current-unit applicability; Fredsborg is withheld despite explicit profile because selected-ID scope remains unresolved. NTA name alone not an inquiry process. Lilla Park transition and historical profile require caution. Idun’s arts statement explicitly spans subjects.\n')
print(json.dumps(new,ensure_ascii=False))
