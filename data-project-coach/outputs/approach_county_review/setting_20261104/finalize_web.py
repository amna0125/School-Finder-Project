"""Accept website candidates after manual review (exclusions by candidate index), one quote per school and feature."""
import json,collections,re
c=json.load(open('candidates.json'))
EXCL={54,287,301,678,779,893,928,1027,1072,1217,422,1163,787,163,134,218,89,570,640,  # food: delivered/ambiguous/future
 352,711,  # food focus: generic city policy
 90,91,92,239,321,393,394,448,654,717,1006,1008,1154,1228,1229,1230,1235,1236,1238,1239,1114,  # sports/arts noise
 49,51,560,718,920,
 25,250,294,296,339,428,430,467,478,821,848,939,1005,1153,1170,1184,1222,1237,87,150,151,283,392,420,421,426,653,655,948,940,1233,1194,819,148,  # premises: historical/future/preschool
 249,425,440,490,621,782,  # schoolyard noise/future
 32,760}
NEG={1175,54,287,678,893,928,1027,1072,1217}  # explicit: food not cooked at this school
ALLOW_SHARED=re.compile(r'^I Tyresös grundskolor|^44 procent av de råvaror')
reg={}
for l in open('register.jsonl'):
    r=json.loads(l);reg[r['sid']]=r['resp'].get('included',{}).get('attributes',{}).get('organizerType')
by=collections.defaultdict(set)
for o in c: by[o['quoted_text']].add(o['school_id'])
FMAP={'food_cooked_on_site':'food_cooked_on_site','food_focus':'food_sustainable_or_vegetarian_focus','sports_hall':'facility_sports_hall','arts_science_rooms':'facility_arts_or_science_rooms','premises_new_or_renovated':'premises_new_or_renovated','schoolyard_green':'schoolyard_described','nature_nearby_stated':'nature_nearby_stated'}
GREEN=re.compile(r'skog|natur|gr[öo]n|tr[äa]d|berg|kuper|park|odling|frukt|lummig|b[äa]r',re.I)
out={}
for i,o in enumerate(c):
    f=o['feature']
    if f=='library':continue
    neg=i in NEG
    if i in EXCL and not neg:continue
    shared=len(by[o['quoted_text']])>1
    scope='school page'
    if shared:
        if ALLOW_SHARED.search(o['quoted_text']) and reg.get(o['school_id'])=='KOMMUN':scope='municipality-wide statement'
        else:continue
    feat=FMAP[f];val='no' if neg else 'yes'
    if feat=='schoolyard_described':val='green/natural' if GREEN.search(o['quoted_text']) else 'large/renovated/varied'
    k=(o['school_id'],feat)
    prev=out.get(k)
    if prev and not (val=='green/natural' and prev['value']!='green/natural') and not (neg and prev['value']=='yes'):continue
    out[k]=dict(school_id=o['school_id'],feature=feat,value=val,source_type='School website' if scope=='school page' else 'Municipality website',scope=scope,source_url=o['source_url'],page_title=o['page_title'],accessed_date=o['accessed_date'],quoted_text=o['quoted_text'],candidate_index=i)
# a 'no' at the same school beats an earlier 'yes' only when explicit; delivered-from-elsewhere wins
rows=list(out.values())
json.dump(rows,open('web_features.json','w'),ensure_ascii=False,indent=1)
print(len(rows),collections.Counter((r['feature'],r['value']) for r in rows))
