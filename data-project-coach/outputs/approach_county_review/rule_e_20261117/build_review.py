"""Build Amna's Rule E yes/no review workbook from quotes.json. Codes nothing."""
import json, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
D = '/home/user/proj/outputs/approach_county_review/rule_e_20261117'
q = json.load(open(f'{D}/quotes.json'))
fix = {  # tighter verbatim quotes (still word for word from the saved page, no staff names)
 '17287315': 'Källtorpskolan är en 7-9 skola, med en särskild undervisningsgrupp RSK (resursskolegrupp) och en nystartad AGR-verksamhet från 2024 som kommer att ha 40 elever.',
 '40631085': 'Fittjaskolan är en skola för elever i åk 4-9, anpassad grundskola och en särskild undervisningsgrupp för elever som är i behov av det.',
 '42434583': 'Årskurser: F-9, KSU-grupper för autism',
 '45757947': 'Tallidsskolan är en skola för elever i åk F-3, anpassad grundskola och en särskild undervisningsgrupp för elever som är i behov av det.',
 '83810698': 'På Elinsborgsskolan har vi två klasser per årskurs och en särskild undervisningsgrupp.',
 '84704913': 'Skolan har två mindre undervisningsgrupper.',
 '96646603': 'Kommunal resursskola årskurs F–9 Lommarskolan',
 '82854505': 'Vad erbjuder Resursskolan vid Martinskolan?',
 '62288230': 'Biträdande rektor årskurs 8-9 och kommunövergripande särskild undervisningsgrupp (KÖSU)',
 '72672270': 'Biträdande rektor, elevhälsoteamet, anpassad grundskola, särskild undervisningsgrupp årskurs F–5',
 '78508835': 'Speciallärare i särskild undervisningsgrupp',
 '84520303': 'Biträdande rektor Topasen/Resursgrupper årskurs F-9',
 '14040970': 'Här kan du ta del av Sigfridsborgsskolan, Stavsborgsskolan, Älta skolas samt Resursskolans läsårsdata.',
 '64836806': 'Fornbackaskolan är en F-6-skola med cirka 340 elever. Här finns både grundskola, anpassad grundskola och en kommunövergripande särskild undervisningsgrupp.',
 '72120589': 'Stålhamraskolan är en F-6-skola med cirka 280 elever. Här finns både grundskola, anpassad grundskola och en kommunövergripande särskild undervisningsgrupp.',
}
fix['44836298'] = fix['82047013'] = fix['14040970']; fix['60570294'] = fix['64836806']
KUNSK = ['11496096','16426165','25309669','46796995','63954028','81266343','87425546']
kq = 'Resursskolan Hägersten (appears only in the site menu and news list)'
S = 'Yes, Support (S)'; E_ = 'Yes, Support (E)'; N = 'No'
short = {S:'Yes S', E_:'Yes E', N:'No'}
plan = {  # sid: (group, suggestion, subcategory if yes, why)
 '11914814': (1,S,'Resource group (municipality-run): KÖSU','The school says the KÖSU group is at Rosenborgskolan.'),
 '12187987': (1,S,'Special teaching groups','The school has two special teaching groups.'),
 '15080815': (1,S,'Resource school class (municipality-run)','The trigger case. Resource school provision F-9 at the school.'),
 '15331669': (3,N,'','Only says it has "access to" a special teaching group, which may be at another school. Not counted under the tightened rule.'),
 '17287315': (1,S,'Resource school group (RSK)','Group named on the school\'s own page.'),
 '24561769': (1,S,'Resource group (municipality-run): language disorder','Municipality class for pupils with language disorder is at the school.'),
 '33794207': (1,S,'Resource classes','The school\'s own page lists resource classes.'),
 '40631085': (1,S,'Special teaching group','Group named on the school\'s own page.'),
 '42434583': (1,S,'Resource group (municipality-run): autism','KSU groups for autism listed in the school facts.'),
 '43166282': (1,S,'Small teaching group','A small group for pupils who need special support.'),
 '44046131': (1,S,'Special teaching group','Group named on the school\'s own page.'),
 '44673074': (1,S,'Special teaching group','Group named on the school\'s own page.'),
 '45757947': (1,S,'Special teaching group','Group named on the school\'s own page.'),
 '46616391': (1,S,'Special teaching group (years 1–6)','Local special teaching group.'),
 '58294404': (1,S,'Special teaching groups (SU and regional RSU)','SU group and a regional RSU group at the school.'),
 '58385274': (1,S,'Small teaching groups','Two smaller groups for pupils who need a smaller setting.'),
 '72120589': (1,S,'Resource group (municipality-run)','On Stålhamraskolan\'s own page.'),
 '77314942': (1,S,'Special teaching group','SU group named on the school\'s own page.'),
 '83810698': (1,S,'Special teaching group','Group named on the school\'s own page.'),
 '84704913': (2,N,'','Two smaller teaching groups, but the page does not say they are for pupils who need support. They could be ordinary small groups.'),
 '92284588': (1,S,'Resource groups (municipality-run)','Two municipality groups for years 4–6 and 7–9.'),
 '92347699': (1,S,'Special teaching group','"Our own" special teaching group.'),
 '97402564': (1,S,'Resource group (municipality-run)','For pupils with extensive support needs.'),
 '96646603': (1,'Yes, Support (E)','Resource school (municipality-run)','The page heads the school as a municipal resource school F–9, so maybe E (whole profile is support).'),
 '62288230': (2,'Yes, Support (S)','Resource group (municipality-run): KÖSU','Only seen as a staff role title. The group exists, but the evidence is thin.'),
 '72672270': (2,S,'Special teaching group (F–5)','Only seen as a staff role title.'),
 '78508835': (2,S,'Special teaching group','Only seen as a staff role title.'),
 '84520303': (2,S,'Resource groups (F–9)','Only seen as a staff role title.'),
 '94279206': (2,N,'','No page of its own. The quote is from Sjötorpsskolan\'s page, which already has this coded. Linking it to this unit would mean going by the unit\'s name, which our rules do not allow. I can try to find its own page.'),
 '82854505': (2,N,'','The resource school is the other Martinskolan unit (13954336), which is already coded Support. Rule B.'),
 '53133366': (2,N,'','NPF-aware, low-arousal approach for everyone. No separate group.'),
 '80378022': (2,N,'','Small-group teaching as ordinary support, not a separate group.'),
 '97777849': (2,N,'','Pupils can work in a small group in a learning centre. Not a separate group.'),
 '14040970': (3,N,'','Shared Nacka page. "Resursskolan" is another unit. Rule B.'),
 '44836298': (3,N,'','Shared Nacka page. "Resursskolan" is another unit. Rule B.'),
 '82047013': (3,N,'','Shared Nacka page. "Resursskolan" is another unit. Rule B.'),
 '28845963': (3,N,'','The quote is from Rosenborgskolan\'s page, not Majtorpskolan. Rule B.'),
 '64836806': (3,N,'','Shared Södertälje list. The sentence is about Fornbackaskolan. Rule B.'),
 '60570294': (3,N,'','Shared Södertälje list. The sentence is about Fornbackaskolan. Rule B.'),
 '25253749': (3,N,'','Mixed-age groups, not support.'), '28184857': (3,N,'','Mixed-age buddy groups, not support.'),
 '62533129': (3,N,'','Flexible groups instead of classes, not support.'), '76557608': (3,N,'','Flexible groups, not support.'),
 '83828066': (3,N,'','Flexible groups, not support.'), '94301041': (3,N,'','Mixed-age after-school groups, not support.'),
 '27595656': (3,N,'','Small classes in general, not a special group.'), '38394561': (3,N,'','Class sizes of 10–20, not a special group.'),
 '87382179': (3,N,'','Small classes in general, not a special group.'), '94943347': (3,N,'','Fairly small classes in general.'),
 '92750123': (3,N,'','Smaller groups in two subjects for everyone.'), '77656740': (3,N,'','Small classes in general.'),
 '32585503': (3,N,'','Staff NPF training only.'), '39351914': (3,N,'','Staff NPF training only.'),
 '46518352': (3,N,'','Staff NPF training only.'), '72345466': (3,N,'','Staff NPF training goal only.'),
 '51100048': (3,N,'','"Kommungemensamma" refers to municipal activities, not a group.'),
}
for k in KUNSK: plan[k] = (3,N,'','Menu noise. "Resursskolan Hägersten" is a different Kunskapsskolan unit. Rule A/B.'); fix[k] = kq
assert set(plan) == set(q), set(q) ^ set(plan)
G = {1:'1. Likely yes', 2:'2. Your judgement', 3:'3. Likely no'}
wb = Workbook(); ws = wb.active; ws.title = 'Review'
hdr = ['Group','School','School ID','Current label','Current approach codes','Quote from the saved page (word for word)','Source page','My decision','Subcategory if yes','Why','Your decision','Your note']
ws.append(hdr)
fills = {1:'E8F5E9', 2:'FFF8E1', 3:'F5F5F5'}
rows = sorted(q, key=lambda k: (plan[k][0], q[k]['name']))
for k in rows:
    g, sug, sub, why = plan[k]; v = q[k]
    ws.append([G[g], v['name'], k, v['state'], v['codes'] or '(none)', fix.get(k, v['quote']), v['url'] or 'https://www.botkyrka.se/tallidsskolan', sug, sub, why, short[sug], ''])
    for c in ws[ws.max_row]: c.fill = PatternFill('solid', fgColor=fills[g])
dv = DataValidation(type='list', formula1='"Yes S,Yes E,No,Unsure"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'K2:K{ws.max_row}')
thin = Side(style='thin', color='CCCCCC')
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='37474F'); c.alignment = Alignment(wrap_text=True, vertical='center')
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(bottom=thin)
    row[10].fill = PatternFill('solid', fgColor='FFFFFF'); row[10].border = Border(left=Side(style='medium', color='1E88E5'), right=Side(style='medium', color='1E88E5'), bottom=thin)
for col, w in zip('ABCDEFGHIJKL', [16,26,11,16,30,60,40,16,28,40,14,30]): ws.column_dimensions[col].width = w
ws.freeze_panes = 'C2'; ws.auto_filter.ref = ws.dimensions
for r in range(2, ws.max_row + 1):
    u = ws.cell(r, 7).value; ws.cell(r, 7).hyperlink = u; ws.cell(r, 7).font = Font(color='1E63B5', underline='single')
# ---- Sheet 2: existing Support codes about groups or teaching, checked against the same line
import duckdb
db = duckdb.connect('/home/user/proj/.state/schools.duckdb', read_only=True)
ex = {r[0]: r for r in db.execute("""select c.code_id, c.school_id, s.name, c.subcategory, c.coding_level, e.quoted_text, e.source_url
 from Approach_codes c join schools s on s.school_unit_code=c.school_id left join Approach_evidence e on e.evidence_id=c.evidence_id
 where c.category like 'Support%'""").fetchall()}
by = {(r[1], r[3]): r for r in ex.values()}
K, TS, TE, R = 'Keep', 'Change to S', 'Change to E', 'Remove'
chk = [  # (school_id, subcategory, decision, why)
 ('69195602','Municipal special teaching group',TE,'The unit itself is the municipality group ("Vi är en så kallad kommungemensam särskild undervisningsgrupp"), so the whole profile is support.'),
 ('37416253','Additional special teaching group for pupils with greater support needs',TS,'A group at an ordinary school. E is only for a whole resource school.'),
 ('39453214','Attached lärstudio / special teaching group only',TS,'A central group attached to an ordinary school. E is only for a whole resource school.'),
 ('72627865','Hearing-impairment classes',TS,'Classes at an ordinary school. E is only for a whole resource school.'),
 ('52217632','Municipal special teaching groups for autism',TS,'Groups at an ordinary school. E is only for a whole resource school.'),
 ('37796564','Regional special teaching groups (RSU); restricted placements',TS,'Groups at an ordinary school. E is only for a whole resource school.'),
 ('23617768','Flexible small teaching groups',R,'Flexible grouping for everyone, not a support group. Same line as Bobergsskolan and Lindeskolan.'),
 ('47640376','Individual action plans and learning centre',R,'Support in a learning centre for any pupil. Same line as Tallbohovskolan.'),
 ('20563782','Differentiated teaching and movement emphasis',R,'Differentiated teaching is a general requirement, not a separate group.'),
 ('19377571','Daylong visual supports and accessible learning',R,'Visual supports and smaller groups for everyone. Accessible teaching is expected of every school.'),
 ('57755652','Visual support and predictable routines',R,'Visual supports in every classroom. Expected of every school.'),
 ('43632318','Structured, accessible teaching and multi-teacher support',R,'Structured teaching with visual support for everyone. Expected of every school.'),
 ('49762104','Predictable, accessible teacher-led teaching',R,'Accessible teaching for everyone. Expected of every school.'),
 ('98070480','Tydliggörande pedagogik',R,'Used for all pupils, alongside cooperative learning, at an ordinary school. Not a separate group.'),
 ('13582062','Additional teaching support',R,'Homework help and two teachers per class. Staffing, not a support group.'),
 ('42149666','Multi-teacher system and common lesson structure',R,'Staffing model, not a support group.'),
 ('56568612','Three-teacher model F–6; two-teacher 7–9',R,'Staffing model, not a support group.'),
 ('37556682','Two adults per lesson / two-teacher Swedish',R,'Staffing model, not a support group.'),
 ('51210001','Two-teacher teaching and half-class practical subjects',R,'Staffing model, not a support group.'),
 ('82110758','MVP and Agera; special teaching groups',K,'Keep for MVP and Agera (named programmes). The quote does not mention a special group, so I will drop "special teaching groups" from the subcategory.'),
 ('71754599','Accessible teaching; special teaching group',K,'Names its own special teaching group.'),
 ('12407147','Special teaching group',K,'Names its own special teaching group.'),
 ('92007673','Special teaching group (Supernova)',K,'Names its own special teaching group.'),
 ('86597125','Studio 19; NPF-trained staff',K,'A named small setting for pupils who need it.'),
 ('74631147','Studios (small settings)',K,'A named small setting for pupils who need it.'),
 ('94902263','Täppan small-group setting',K,'A named small setting for pupils in years 1–6.'),
 ('61061763','Språkspåret (language-disorder track)',K,'A standing language-disorder group with its own rooms.'),
 ('99373839','A-spår (autism track)',K,'A standing autism group.'),
 ('66383692','Smaller groups; on-site resource school',K,'A municipality resource school at the school.'),
 ('46646143','Conductive pedagogy and communication profiles',K,'A specialised profile for pupils with disabilities.'),
]
h2 = wb.create_sheet('Already coded')
h2.append(['School','School ID','Current subcategory','Current level','Quote on file','Source page','My decision','Why','Your decision','Your note'])
for sid, sub, dec, why in chk:
    r = by[(sid, sub)]
    h2.append([r[2], sid, sub, r[4], (r[5] or '')[:300], r[6], dec, why, dec, ''])
dv2 = DataValidation(type='list', formula1='"Keep,Change to S,Change to E,Remove"', allow_blank=True); h2.add_data_validation(dv2); dv2.add(f'I2:I{h2.max_row}')
for c in h2[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='37474F'); c.alignment = Alignment(wrap_text=True, vertical='center')
col = {K:'E8F5E9', TS:'FFF8E1', TE:'FFF8E1', R:'FDECEA'}
for row in h2.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(bottom=thin); c.fill = PatternFill('solid', fgColor=col[row[6].value])
    row[8].fill = PatternFill('solid', fgColor='FFFFFF'); row[8].border = Border(left=Side(style='medium', color='1E88E5'), right=Side(style='medium', color='1E88E5'), bottom=thin)
    row[5].hyperlink = row[5].value; row[5].font = Font(color='1E63B5', underline='single')
for c, w in zip('ABCDEFGHIJ', [26,11,30,11,55,40,15,45,15,30]): h2.column_dimensions[c].width = w
h2.freeze_panes = 'B2'; h2.auto_filter.ref = h2.dimensions
# ---- Sheet 3: the standard
h = wb.create_sheet('Standard')
for line in ['Rule E standard (tightened 18 November 2026)', '',
 'Legal basis: skollagen chapter 3. Every school must give extra adaptations and special support. The principal may decide, pupil by pupil, that support is given one to one or in a special teaching group (3 kap. 11 §), which can be at another school.',
 'So every school must be ABLE to give support in a smaller group. No school is required to RUN a standing group. Only a standing group sets a school apart.', '',
 'Count at E: the whole school is a resource school, or the unit itself is the group.',
 'Count at S: the school\'s own page (or a sentence about this school on a shared page) names a standing group or class AT this school for pupils who need support:',
 '  resursklass, särskild undervisningsgrupp, KSU/KÖSU/RSU, an autism or language-disorder group, or a named studio or small setting for pupils who need a smaller context.',
 '  A staff job title naming the group on the school\'s own page counts. Staff names are never stored.', '',
 'Do not count:', '  support "in small groups or individually when needed", extra adaptations, elevhälsa, special educators',
 '  generally small classes, flexible or mixed-age groups, two-teacher or multi-teacher staffing',
 '  differentiated, structured or visual-support teaching for all pupils, staff NPF training, a low-arousal approach',
 '  "access to" a group somewhere else, anpassad grundskola (a separate school form), groups for newly arrived pupils, a group whose purpose is not stated',
 '  a group at another unit on a shared page (Rule B)', '',
 'Not part of Rule E: named wellbeing programmes (Trivselledare, Olweus, PAX, IBIS and similar) stay as they are.', '',
 'How to use this file: "My decision" is filled in, and "Your decision" starts as a copy of it. Change "Your decision" wherever you disagree. I will load whatever "Your decision" says.',
 'Sheet "Review": 63 schools found by the keyword scan that do not have Support yet.',
 'Sheet "Already coded": existing Support codes about groups or teaching, checked against the same line. Wellbeing programmes were not re-checked.',
 'Not covered: 13 schools have no saved page text.']:
    h.append([line])
h.column_dimensions['A'].width = 150; h['A1'].font = Font(bold=True, size=13)
for r in h.iter_rows(): r[0].alignment = Alignment(wrap_text=True)
wb.move_sheet('Standard', offset=-2)
out = f'{D}/rule_e_review_20261118.xlsx'; wb.save(out)
import collections
print(out, collections.Counter(plan[k][1] for k in q), collections.Counter(x[2] for x in chk))
