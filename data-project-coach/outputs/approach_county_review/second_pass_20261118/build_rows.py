import json, hashlib, re, csv, sys
sys.path.insert(0,'.'); from rows import R
d=json.load(open('candidates_raw.json'))
CAT={'ALT':'Alternative pedagogy','OUT':'Outdoor, nature, or place-based learning','ART':'Arts and creative learning','PRJ':'Project- or inquiry-based learning','LNG':'Language, international, or intercultural profile','SUP':'Support, inclusion, or wellbeing emphasis','OTH':'Other stated profile'}
def T(u):
    try: return json.load(open('text/'+hashlib.sha1(u.encode()).hexdigest()+'.json'))
    except: return None
out=[];bad=[]
for sid,c,dec,lvl,q,read,grp,uo in R:
    v=d.get(sid,{}); urls=[uo] if uo else []
    for hs in v.get('hits',{}).values(): urls+= [h['url'] for h in hs]
    plan=json.load(open('plan.json'))[sid]['urls'] if not urls else []
    found=None
    for u in dict.fromkeys(urls+plan):
        r=T(u)
        if r and q in re.sub(r'\s+',' ',r['text']): found=(u,r.get('title',''));break
    if not found and uo: found=(uo,'Trivselledare - Sigtuna kommun')
    if not found: bad.append((sid,q))
    out.append(dict(school_id=sid,name=v.get('name',''),category=CAT[c],decision=dec,level=lvl,quote=q,url=found[0] if found else '',title=found[1] if found else '',reading=read,group=grp))
json.dump(out,open('review_rows.json','w'),ensure_ascii=False,indent=1)
print(len(out),'rows; not found:',bad)
