"""Stage Batch28 only; no database or county-ledger writes."""
import csv, hashlib, json, re
from pathlib import Path
from html import unescape
from outputs.approach_county_review.extract19 import parse
from school_pipeline.approach_migration import validate_records
P=Path('outputs/approach_county_review/batch28_10schools_20261102')
DATE='2026-11-02'
def save(n,v):
    target=P/n
    assert not target.exists(), str(target)
    target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
selection=json.loads((P/'selection.json').read_text())
ids=[x['school_id'] for x in selection]
assert len(ids)==len(set(ids))==10 and ids==sorted(ids)
sources={
'farentuna':('43038662','https://www.ekero.se/forskola-skola/grundskola/skolor-i-ekero-kommun/farentuna-skola-f-6',200),
'bjorkhagen':('43088454','https://grundskola.stockholm/hitta-grundskola/grundskola/bjorkhagens-skola',200),
'bergshamra':('43133926','https://www.solna.se/barn--utbildning/grundskola/hitta-grundskola/bergshamraskolan',200),
'vittra':('43138370','https://vittra.se/brotorp/',200),
'vittra_school':('43138370','https://vittra.se/brotorp/om/grundskola/',200),
'nakter':('43140379','https://nakterhusskolan.haninge.se/',200),
'nakter_method':('43140379','https://nakterhusskolan.haninge.se/var-skola/om-skolan/',200),
'nakter_work':('43140379','https://nakterhusskolan.haninge.se/sa-har-jobbar-vi/',200),
'nalsta':('43166282','https://grundskola.stockholm/hitta-grundskola/grundskola/nalstaskolan',200),
'saltangen':('43245047','https://www.nacka.se/valfard-skola/saltsjo-duvnas-skola/',404),
'saltangen_current':('43245047','https://www.nacka.se/valfard-skola/saltangens-skola/',200),
'saltangen_method':('43245047','https://www.nacka.se/valfard-skola/saltangens-skola/pedagogisk-inriktning/',200),
'vasaskolan':('43289917','https://www.danderyd.se/skolor/vasaskolan/',200),
'vasa_reading':('43289917','https://www.danderyd.se/skolor/vasaskolan/satsningar/las--och-litteratursatsning/',200),
'vasa_nta':('43289917','https://www.danderyd.se/skolor/vasaskolan/satsningar/naturvetenskap--teknik-for-alla/',200),
'ralsen':('43375546','https://www.ralsen.se/',200),
'ralsen49':('43375546','https://4-9.ralsen.se/v%C3%A5ra-verksamheter/skolan',200)}
texts={}; logs=[]
for name,(sid,url,status) in sources.items():
    path=P/'sources'/(name+'.html'); raw=path.read_text(); text,links=parse(path); texts[name]=text
    title=unescape(re.search(r'<title[^>]*>(.*?)</title>',raw,re.S|re.I).group(1)).strip()
    logs.append(dict(school_id=sid,source_url=url,final_url=url,page_title=title,accessed_date=DATE,http_status=status,source_file=str(path.relative_to(P)),review_scope='Public school description / relevant pedagogy pages only; not exhaustive',selection_rationale='Official directory ID order; school/provider/municipal source. No profiles transferred across units.'))
e=[];c=[]
def evidence(name,quote,note):
    sid,url,_=sources[name];assert quote in texts[name], (name,quote)
    eid=f'ae_b28_{sid}_{1+sum(x["school_id"]==sid for x in e):02d}'
    title=next(x['page_title'] for x in logs if x['source_file']==f'sources/{name}.html')
    e.append(dict(evidence_id=eid,school_id=sid,source_url=url,page_title=title,accessed_date=DATE,quoted_text=quote,evidence_type='School webpage',interpretation_note=note));return eid

evidence('bergshamra','Skolan har även ett gott samarbete med Solna kulturskola.','Unclear/Low: isolated cooperation statement does not establish sustained arts integration. Official snapshot years1–7; website F–9 and phased reopening from year7 autumn2025, expanding one year annually. Do not treat F–9 as verified current provision in every year.')
evidence('vittra_school','Vi arbetar tematiskt när det passar och väver samman ämnen för att skapa mening i lärandet.','Unclear/Low: conditional thematic work in lower/middle and upper-school sections; no sufficiently concrete sustained inquiry/project process described in reviewed page. No arts code from ordinary aesthetic subjects. School F–9 distinguished from preschool.')
evidence('ralsen49','Eleverna använder fysiska läroböcker i nästan alla ämnen, och på mellanstadiet satsar vi särskilt mycket på läsning, som vi ser som en viktig grund inför högstadiet.','Unclear/Low: reading emphasis specifically middle school, insufficient concrete model for a firm code. Provider homepage explicitly links Rälsen4–9 to this subdomain; no transfer from other provider units. About140 pupils is self-reported for26/27, not class size.')
a=evidence('vasa_nta','Det viktigaste är det undersökande arbetssättet som sporrar eleverna att själva ställa frågor, göra förutsägelser, genomföra sina undersökningar och dokumentera resultatet.','Explicit named NTA inquiry approach. School self-description, not independently verified practice.')
b=evidence('vasa_nta','Vasaskolan var först ut i kommunen med att använda NTA, och arbetar sedan 2004 kontinuerligt med arbetssättet i alla klasser.','Direct unit applicability statement; historical start date is school wording, not independent verification.')
d=evidence('vasa_reading','Under varje läsår satsar vi extra mycket på läsning för eleverna i år 2 (vårterminen), 3 (höstterminen) och år 4 då vi har läsgrupper.','Targeted reading/literature initiative; extra reading groups specifically year2 spring, year3 autumn and year4. Not an arts or language/international profile.')
for cat,sub,eid,note in [('Project- or inquiry-based learning','NTA inquiry',a,'All classes per applicability excerpt '+b),('Other stated profile','Reading and literature initiative',d,'Extra reading groups only specified years/terms; do not generalize this component to all years.')]:
 c.append(dict(code_id=f'ac_b28_43289917_{len(c)+1:02d}',school_id='43289917',category=cat,subcategory=sub,coding_level='Explicit',confidence='High',evidence_id=eid,coder_note='Assistant contextual review, 2026-11-02, codebook v1 categories/thresholds. '+note+' Reviewed claims are not verified implementation or effects.',review_status='Reviewed'))
N='No clear evidence within scoped review';U='Uncertain evidence / requires review';R='Reviewed approach claim';B='Permission blocker'
decisions=[
(N,'clear_for_reviewed_page','General safety/learning aims; rural location alone not outdoor pedagogy. Review limited to municipal school page; no dedicated pedagogy link identified.',''),
(N,'clear_for_reviewed_page','School F–9 page reviewed. Teamwork, routines, support and safety wording do not establish distinctive approach; no firm code. Preschool-class staffing/count wording not generalized to compulsory years.',''),
(U,'requires_review_grade_timing','Isolated kulturskola cooperation; no firm arts code. Official years1–7 versus website F–9 phased expansion.','Clarify grade provision and substantive arts cooperation if needed.'),
(U,'clear_for_reviewed_school_page','F–9 school-specific page distinguishes preschool. Conditional thematic work insufficient for firm sustained inquiry label.','Further concrete pedagogy evidence needed before coding.'),
(N,'clear_for_reviewed_pages','Homepage, about and work-method page: generic outcomes, adaptation and cooperation; ordinary subject facilities not arts evidence. Dated2023 descriptions retained.',''),
(N,'clear_for_reviewed_page','F–6 page reviewed; nearby outdoor spaces, facilities and fritids creativity do not establish school-wide outdoor/arts approach. Small support group not generalized.',''),
(B,'not_assessed_permission_blocker','Existing terms_review_required retained; no school content fetched or coded.','Resolve applicable terms before further collection.'),
(N,'school_name_and_grades_match_registered_link_stale','Registered Saltsjö-Duvnäs URL404. Current official Saltängens F–3 page and pedagogy page match name/year range; individual adaptation/expectations not distinctive approach. No profile transfer from Saltsjö-Duvnäs.','Registered-link correction and official identity/address reconciliation remain follow-up; no definitive ID verification claimed.'),
(R,'clear_with_code_specific_year_limits','Vasaskolan F–6; NTA all classes, reading groups specific years/terms. Two firm codes, no effectiveness inference.',''),
(U,'clear_provider_to_unit_link','Provider explicitly links Rälsen4–9 subdomain; school page years4–9. Reading emphasis middle school insufficiently specific for firm code.','Clarify sustained reading model before coding.')]
reviews=[]
for row,(outcome,scope,note,follow) in zip(selection,decisions):
 sid=row['school_id'];reviews.append(dict(school_id=sid,official_directory_name=row['official_directory_name'],registered_url=row['registered_url'],outcome=outcome,scope_status=scope,reviewer='Assistant; not human or independent practice verification',review_date=DATE,pages_reviewed='; '.join(x['source_url'] for x in logs if x['school_id']==sid),note=note,unresolved_follow_up=follow,batch_reference='batch28_10schools_20261102'))
validate_records(e,c)
assert {r['school_id'] for r in reviews}==set(ids)
save('Approach_evidence.staged.json',e);save('Approach_codes.staged.json',c)
for name,rows in [('review_log.csv',reviews),('collection_log.csv',logs)]:
 with (P/name).open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('collection_log.json',logs)
save('source_hashes.json',[dict(file=str(f.relative_to(P)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted((P/'sources').iterdir()) if f.is_file()])
save('staging_validation.json',dict(schema_validation='passed',quote_substrings='passed',unique_schools=10,evidence_records=len(e),code_records=len(c),database_modified=False,county_ledger_modified=False))
status=json.loads((P/'batch_status.json').read_text());assert status['status']=='COLLECTION_IN_PROGRESS'
save('batch_status.before_staging.json',status)
status.update(status='STAGED_VALIDATED_NOT_LOADED',evidence_records=len(e),code_records=len(c),outcomes={v:sum(r['outcome']==v for r in reviews) for v in [R,U,N,B]})
(P/'batch_status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
(P/'REPORT.md').write_text('# Batch28 — structured staging only\n\n10 schools; 6 evidence records; 2 codes. One reviewed-claim school, three uncertain, five scoped no-clear, one permission blocker. Source access: 2026-11-02.\n\nNot loaded, replayed or county-checkpointed. Batch27 remains separately staged, not loaded/checkpointed. Last verified county checkpoint remains Batch26:273 documented/489 pending/762. No Batch29 started.\n\nScope status is separate from approach outcome. These ten qualitative scope notes are not an all-checked-schools scope audit or a binary scope count.\n\nPermissions: Björkhaga retained terms blocker with no content retrieval. Stockholm robots response malformed, not affirmative clearance. Rälsen root/subdomain robots404 pages are not robots policies. Other saved robots have no identified intended-path prohibition; exhaustive terms clearance is not asserted. No controls bypassed. Search results used only for discovery, not evidence. Social, jobs, galleries, logins and application pages excluded.\n\nAll sources and exact quotes are in collection/evidence tables; raw response bytes hashed. No precise fetch times invented. Generic claims and ordinary activities excluded conservatively. School wording does not verify implementation or causal effects.\n')
(P/'decision_log.md').write_text('# Batch28 decisions\n\n'+ '\n\n'.join(r['school_id']+' — '+r['outcome']+'\n'+r['note']+'\nFollow-up: '+r['unresolved_follow_up'] for r in reviews)+'\n\nCodebook v1 draft multiple-evidence repeated-code suggestion conflicts with current uniqueness validator. As in Batch27, one code per school/category/subcategory is used with supplementary evidence IDs in coder_note; no codebook or validator changes.\n')
print(json.dumps(status,ensure_ascii=False))
