"""Finalize batch02 review artifacts; no database operations or network requests."""
from pathlib import Path
import csv, json, re, html, hashlib, io
from collections import Counter
ROOT=Path('outputs/approach_county_review')
B=ROOT/'batch02_10schools_20261027'
DATE='2026-10-27'
def dump(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(file):
    s=(B/file).read_text(encoding='utf-8')
    s=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S)
    return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def title(file):
    s=(B/file).read_text(encoding='utf-8')
    return html.unescape(re.search(r'<title[^>]*>(.*?)</title>',s,re.S).group(1)).strip()
def csvwrite(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
selection=json.loads((B/'selection.json').read_text())
schools=selection['schools']
assert len(schools)==10 and len({s['school_id'] for s in schools})==10
bot='https://www.botkyrka.se/forskola-och-skola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/'
stock='https://grundskola.stockholm/hitta-grundskola/grundskola/'
urls={
'eleonora.html':bot+'eleonoraskolan', 'tullinge.html':bot+'tullingebergsskolan', 'skogsback.html':bot+'skogsbacksskolan',
'stenhamra.html':'https://www.ekero.se/forskola-skola/grundskola/skolor-i-ekero-kommun/stenhamraskolan-f-6',
'sia.html':'https://siaskolan.se', 'sia_about.html':'https://siaskolan.se/om-sia-skolan/', 'sia_hagersten.html':'https://siaskolan.se/sia-hagersten/',
'samskola.html':'https://www.nacka.se/valfard-skola/saltsjobadens-samskola-f9/',
'samskola_erasmus.html':'https://www.nacka.se/valfard-skola/saltsjobadens-samskola-f9/for-vardnadshavare/erasmus2/',
'katarina.html':stock+'katarina-sodra-skola', 'ulvsattra.html':'https://www.jarfalla.se/forskolaskolaochutbildning/grundskola/grundskola/kallhallstaket/ulvsattraskolan.4.36ac70f31639ecd947f2f28.html',
'sjoang.html':stock+'sjoangsskolan', 'eken.html':stock+'ekens-skola'}
# Short literal quotations checked against decoded saved responses below.
claims=[
('10184517','eleonora.html','Other stated profile','Mathematics, science and digital competence',
'Skolan har en matematisk och naturvetenskaplig inriktning med fokus på digital kompetens.',
'Page explicitly names this profile and describes extra mathematics/science teaching time. Ordinary F–9 school link identifies 10184517; adapted-school provision is not transferred. Optional After School activities do not establish an arts approach.'),
('10657244','skogsback.html','Other stated profile','Football and basketball; years 4–9',
'Skogsbacksskolan har två specialinriktningar för elever i årskurs 4-9, en fotboll- och en basketprofil.',
'Explicit optional/profile provision scoped to years 4–9, not every pupil or all years. Ordinary-school link identifies 10657244; adapted school 10921100 excluded. Generic support claims and MVP alone not coded as a separate school-wide wellbeing emphasis.'),
('11777750','samskola_erasmus.html','Language, international, or intercultural profile','Erasmus+ exchange and partnership programme',
'Samskolan har ett aktivt Erasmussamarbete där vi erbjuder våra elever utbytesresor till olika länder i Europa, tar emot gäster ifrån våra partnerskolor samt möjliggör för fortbildning för våra lärare.',
'Concrete ongoing international exchange provision, not an inference from a single news item. Official unit is F–9; page does not establish participant year groups, universal participation, language of instruction or an international curriculum. Code limited to the stated programme.'),
('13301127','eken.html','Other stated profile','Ämnesveckor / concentrated subject-week timetable',
'På Ekens skola arbetar du enligt schemamodellen ämnesveckor. Det innebär att du läser koncentrerat ett teoretiskt ämne i rullande femveckorsperioder.',
'Explicit named scheduling model for years 7–9, corroborated by official unit page and school link. Not classified as project/inquiry-based learning or Alternative pedagogy; does not prove either. Practical/aesthetic subjects weekly are an ordinary subject description, not an arts-learning profile.')]
evidence=[];codes=[]
for sid,file,cat,sub,quote,note in claims:
    assert quote in text(file),(sid,'quotation not in saved response')
    eid='ae_b02_'+sid+'_01';cid='ac_b02_'+sid+'_01'
    evidence.append(dict(evidence_id=eid,school_id=sid,source_url=urls[file],page_title=title(file),accessed_date=DATE,quoted_text=quote,evidence_type='School website self-description',interpretation_note=note))
    codes.append(dict(code_id=cid,school_id=sid,category=cat,subcategory=sub,coding_level='Explicit',confidence='High',evidence_id=eid,coder_note=note+' Codebook v1 draft; assistant contextual review and consistency pass on '+DATE+'. Reviewed means source/coding review, not human sign-off or independently verified practice.',review_status='Reviewed'))
# Each school has a bounded review outcome even when no firm code is justified.
config={
'10184517':(['eleonora.html'],'Reviewed explicit claim','F–9 ordinary school; exact ID linked on municipality page','No unresolved claim-scope blocker; profile does not imply universal participation in optional After School.'),
'10495223':(['tullinge.html'],'Scoped no clear approach evidence','F–5 ordinary school 10495223 linked separately from adapted unit 30031281','Generic safety/learning, planned breaks and movement insufficient for distinctive school-wide category. Adapted years 1–9 and special teaching group not generalized.'),
'10657244':(['skogsback.html'],'Reviewed explicit claim','F–9 ordinary unit exact ID linked; sports years 4–9 only','Facility booking terms flag assessed and cleared as unrelated to website collection; no blanket reuse permission claimed.'),
'11025388':(['stenhamra.html','official_stenhamra.html'],'Scoped no clear approach evidence','F–6 and address confirmed against official unit 11025388','Vision, learning environment and small special teaching group do not establish a school-wide approach.'),
'11442396':(['sia.html','sia_about.html','sia_hagersten.html','official_sia.html'],'Uncertain evidence; Requires review','F–9 Hägersten at Sulvägen matched to official unit; provider also operates Häggvik','International environment/multicultural-background wording at provider level retained as an uncertain lead; concrete unit-specific language/curriculum or intercultural pedagogy not established. No firm code. Robots Crawl-delay 10; requests in separate tool rounds; exact historical timing not independently audited.'),
'11777750':(['samskola.html','samskola_erasmus.html','official_samskola.html'],'Reviewed explicit claim','F–9 official unit identity/address; Erasmus participant years unspecified','Do not infer international curriculum or all-pupil participation. Guessed /om-samskolan/ returned 404 and is excluded. Old samskolan.org permission issue not bypassed; current Nacka official site used.'),
'12187987':(['katarina.html','official_katarina.html'],'Scoped no clear approach evidence','F–6 official unit and school URL match','Values, support groups and attendance team insufficient to establish distinctive school-wide support approach. Culture floor and fritids creativity do not alone establish arts-learning pedagogy.'),
'12801932':(['ulvsattra.html','official_ulvsattra.html'],'Scoped no clear approach evidence','F–6 official unit and matching address confirmed','Bornholmsmodellen scoped to preschool class literacy, not a whole-school alternative pedagogy. Ordinary play, outings, curriculum wording and support provision insufficient. Conflicting pupil counts not used as approach evidence.'),
'13124830':([], 'Prior-source scoped review; fresh source inaccessible; Requires review','Earlier saved text describes Sjöängsskolan F–9; fresh official unit matching not completed in this batch','Fresh sjoang.html unreadable despite HTTP 200. Earlier saved 2026-10-21 text reviewed for learning environment, ordinary aesthetic facilities, fritids and library claims; no firm approach code justified in that scope. Title remains candidate, not verified metadata. Follow-up: readable fresh source/title and official unit confirmation.'),
'13301127':(['eken.html','official_eken.html'],'Reviewed explicit claim','Years 7–9 confirmed against official unit and school URL','No unresolved blocker for the narrowly scoped subject-week code; team sizes are not class sizes.')}
logs=[];reviews=[]
for s in schools:
    sid=s['school_id'];files,outcome,scope,note=config[sid]
    pages=[]
    for file in files:
        url=urls.get(file,'https://utbildningsguiden.skolverket.se/skolenhet?schoolUnitID='+sid)
        pages.append(dict(source_url=url,page_title=title(file),accessed_date=DATE,saved_file=file,sha256=hashlib.sha256((B/file).read_bytes()).hexdigest()))
    if sid=='13124830':
        pages=[dict(source_url=stock+'sjoangsskolan',page_title=None,title_candidate='Sjöängsskolan, F–9 - Stockholms stad',accessed_date='2026-10-21',saved_file='../website_county/13124830_0.txt',sha256=hashlib.sha256(Path('outputs/website_county/13124830_0.txt').read_bytes()).hexdigest(),title_status='Candidate from saved first line, not independently verified')]
    logs.append(dict(school_id=sid,registered_url=s.get('registered_url',''),selection_rationale='Next official-ID-order directory unit lacking prior contextual review; not dashboard sample selection',pages_reviewed=pages,review_date=DATE,outcome=outcome,unit_scope=scope,interpretation_exclusions_and_followups=note,permission_assessment='Public official/provider pages only; no access control bypass. Minimal quotations, links and private audit copies; not blanket reuse clearance. Prior permission flags retained unless specifically assessed. Botkyrka booking terms concern facility hire, not website reuse; SIA robots delay noted.',search_concepts='om skolan/about us; pedagogik/pedagogy; utbildning/education; profil/profile; kreativ/creative; kultur/arts; lärande/learning; värdegrund/values. Contextual text inspection, not claim that each term was a separate web search.',load_status='Not loaded; database disk I/O error'))
    reviews.append(dict(school_id=sid,official_directory_name=s['official_directory_name'],outcome=outcome,evidence_rows=sum(e['school_id']==sid for e in evidence),code_rows=sum(c['school_id']==sid for c in codes),unit_scope=scope,followup_note=note,reviewer='Assistant; not independently verified practice',review_date=DATE,load_status='Not loaded'))
dump(B/'Approach_evidence.staged.json',evidence);dump(B/'Approach_codes.staged.json',codes)
csvwrite(B/'review_log.csv',reviews)
(B/'collection_log.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in logs),encoding='utf-8')
dump(B/'batch_status.json',dict(status='Contextual review recorded for all 10; unresolved follow-ups remain separate',review_date=DATE,selection_file_note='selection.json retained as historical queue snapshot; this file and review_log.csv supersede its queued status',school_ids=[s['school_id'] for s in schools],reviewed_claim_schools=4,scoped_no_clear_evidence_schools=4,requires_review_schools=2,database_error="OperationalError('disk I/O error')",database_writes=False))
# New ledger snapshot preserves initial ledger and every earlier review state.
ledger=list(csv.DictReader((ROOT/'county_progress_20261027.csv').open(encoding='utf-8')))
assert len(ledger)==762 and len({r['school_id'] for r in ledger})==762
old={r['school_id']:dict(r) for r in ledger}
for r in ledger:
    sid=r['school_id']
    if sid in config:
        r['review_state']='Contextual review recorded; '+config[sid][1]
        r['collection_status']='reviewed_claim' if sid in {c['school_id'] for c in codes} else ('requires_review' if 'Requires review' in config[sid][1] else 'scoped_no_clear_evidence')
        r['note']=config[sid][3]+' Staged only, not loaded.'
assert all(r==old[r['school_id']] for r in ledger if r['school_id'] not in config)
csvwrite(ROOT/'county_progress_20261027_after_batch02.csv',ledger)
next_rows=[r for r in sorted(ledger,key=lambda r:r['school_id']) if not (r['review_state'].startswith('Contextual review recorded') or r['review_state'].startswith('Prior contextual') or 'pilot' in r['review_state'].lower())][:10]
dump(ROOT/'next_batch_after_batch02.json',dict(status='Selected only; not reviewed or loaded',selection_rule='First 10 official IDs without documented prior contextual/pilot review; includes blockers',schools=next_rows))
# Validation against directory ledger and exact saved quotations, not database claims.
ids={r['school_id'] for r in ledger};emap={e['evidence_id']:e for e in evidence}
assert len(emap)==len(evidence)==4 and len({c['code_id'] for c in codes})==4
for c in codes:
    assert c['school_id'] in ids and c['school_id']==emap[c['evidence_id']]['school_id']
    assert c['category'] in {'Other stated profile','Language, international, or intercultural profile'}
    assert (c['coding_level'],c['confidence'],c['review_status'])==('Explicit','High','Reviewed')
assert len(reviews)==10 and len({r['school_id'] for r in reviews})==10
assert not ({r['school_id'] for r in next_rows}&set(config))
dump(B/'validation.json',dict(status='Passed artifact assertions',schools=10,evidence_rows=4,code_rows=4,schools_with_codes=4,scoped_no_clear_evidence=4,requires_review=2,ledger_rows=762,prior_nonbatch_ledger_rows_unchanged=752,exact_quotes_checked_against_saved_html=True,checks=['Unique school/evidence/code IDs','Official-directory membership','Code/evidence school agreement','Allowed category/level/confidence/status','Four exact quotation matches','Ten outcomes','Prior nonbatch ledger rows unchanged','Next selection disjoint'],database_validation='Not performed; read-only quick_check raised disk I/O error',database_writes=False))
(B/'decision_log.md').write_text('''# Batch02 decisions — 2026-10-27
Reviewer: assistant, against codebook v1 draft. Reviewed means website claim/coding review, not observed practice.

- Eleonora: mathematical/science/digital profile explicit. Optional After School creativity excluded from arts code. Exact ordinary-school ID linked on municipality page.
- Skogsback: football/basketball profile explicitly years 4–9; one scoped code with both labels. Adapted-school and preschool provision excluded. MVP and general support do not automatically establish a school-wide inclusion approach.
- Samskolan: active Erasmus exchanges/partners/teacher development qualify as an explicit international programme, not an international curriculum. Participation years remain unspecified and are stated as a code caveat.
- Eken: named ämnesveckor model belongs under Other stated profile. Concentrated timetable alone does not establish inquiry/project learning or alternative pedagogy. Team of 150 not class size.
- SIA: provider's international environment statement retained as an uncertain lead. Unit page matched to Hägersten, but does not substantiate a specific international/intercultural teaching approach. No firm code.
- Tullinge, Stenhamra, Katarina, Ulvsättra: no clear approach found within listed page/section scope; not proof of absence. Ordinary duties/support, subject lists, outings and facilities do not suffice. Ulvsättra's Bornholmsmodellen describes preschool-class literacy, not a school-wide alternative pedagogy.
- Sjöäng: earlier saved text reviewed, but title candidate and fresh unreadable response prevent source finalization. No invented metadata or code. Keep fresh-source and unit matching follow-up explicit.
- Botkyrka terms: inspected booking page main text concerns hyrestagare, booked facilities, safety, damage and hiring eligibility. Not website collection terms. This resolves that particular automated terms-link flag, not all reuse/legal questions.
- Permissions: SIA Crawl-delay 10 noted; this run used separate request rounds, but historical timing is not independently audited. No controls bypassed. Old samskolan.org not retried. Failed guessed Samskolan about URL retained as 404 exclusion.
- Second consistency pass: four exact quotes and code mappings checked; no codes generated for remaining six units, and no quality/causal conclusions.
''',encoding='utf-8')
lines=['# Batch02 contextual review — 27 October 2026','','All 10 units now have documented outcomes. This finishes the batch review artifact, not every follow-up and not database loading.','','- 4 evidence rows and 4 linked Explicit/High Reviewed codes across 4 schools.','- 4 scoped no-clear-evidence outcomes; 2 Requires review outcomes (SIA and Sjöäng).','- Files are batch-only staged rows, not replacement snapshots for prior batches and not loaded.','- Read-only database quick_check still raised disk I/O error. No database writes, backup, repair or loader success claimed.','','| School ID | School | Outcome |','|---|---|---|']
lines += [f"| {r['school_id']} | {r['official_directory_name']} | {r['outcome']} |" for r in reviews]
lines += ['','## Continuation','Canonical new ledger: `../county_progress_20261027_after_batch02.csv` (762 unique IDs). Initial ledger and selection.json preserved as historical queue snapshots. `../next_batch_after_batch02.json` identifies the next 10; no contextual reviews performed for that selection. Prior 20 contextual reviews and 3 pilots are preserved, not revalidated here. No county-completion claim.','','## Audit and limitations','See collection_log.jsonl for URLs, actual titles/access dates, scopes, permission notes and exclusions; decision_log.md for borderline interpretations; validation.json for artifact assertions. Saved HTML titles and quotes checked; past access timing not inferred from review timestamps. Sjöäng uses earlier source access 2026-10-21 and unverified title candidate only in collection log, not in an evidence row. All school claims are self-description, not verified teaching practice.','', '## Source links']
lines += [f"- {e['school_id']}: [{e['page_title']}]({e['source_url']}) (accessed {e['accessed_date']})." for e in evidence]
(B/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(validation='passed',reviewed_outcomes=len(reviews),evidence=len(evidence),codes=len(codes),next_ids=[r['school_id'] for r in next_rows],states=dict(Counter(r['review_state'].split(';')[0] for r in ledger))),ensure_ascii=False))
