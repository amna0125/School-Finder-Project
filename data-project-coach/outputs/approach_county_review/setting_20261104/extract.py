"""Website pass for school setting: candidate sentences per feature from saved school pages (pattern match, then manual check)."""
import json,re,sys,csv
from pathlib import Path
HERE=Path(__file__).resolve().parent;SR=HERE.parent/'single_run_20261103'
sys.path.insert(0,str(SR))
from fetch import name_tokens,fold
F={
 'food_cooked_on_site':r'tillagningsk[öo]k|(lagar|tillagar|tillagas|lagas)\b[^.]{0,40}\b(fr[åa]n grunden|p[åa] plats|p[åa] skolan|i (v[åa]rt|skolans|eget) (egna )?k[öo]k|sj[äa]lva)|\beget k[öo]k|egen kock|v[åa]ra kockar|v[åa]r kock|\bk[öo]ket lagar',
 'food_focus':r'ekologisk[a]? (mat|r[åa]varor|livsmedel)|n[äa]rproducerad|vegetarisk[a]? (mat|alternativ|dag)|klimatsmart[a]? mat|svensk[a]? r[åa]varor',
 'library':r'skolbibliotek|\bbibliotek(et)?\b[^.]{0,60}(skolan|elever|l[äa]s|l[åa]n|bibliotekarie)|bibliotekarie',
 'sports_hall':r'idrottshall|gymnastiksal|sporthall|idrottssal|\bgympasal|fullstor hall|egen hall',
 'arts_science_rooms':r'musiksal|slöjdsal|tr[äa]sl[öo]jd|textilsl[öo]jd|bildsal|atelj[ée]|no-sal|laborator|\blabb\b|makerspace|teatersal|\baula\b|danssal|musikstudio|replokal',
 'premises_new_or_renovated':r'nybyggd|nyrenoverad|nyrenoverade|nybyggda|renoverad[e]?\b|nya lokaler|moderna lokaler|byggs om|byggs ut|tillbyggnad|ny skolbyggnad|invigdes|nyinvigd',
 'schoolyard_green':r'sk?olg[åa]rd(en|ar)?\b[^.]{0,80}\b(gr[öo]n|skog|natur|tr[äa]d|lummig|kuper|klippor|berg|odling|upprust|rustades|renover|ny|stor|rymlig)|(gr[öo]n|stor|rymlig|lummig|naturnära|ny|nyrenoverad|upprustad) sk?olg[åa]rd',
 'nature_nearby_stated':r'(n[äa]rhet till|n[äa]ra|n[äa]ra till|granne med|ligger vid|omgiven av|alldeles intill|runt h[öo]rnet)[^.]{0,40}\b(skog|skogen|natur|naturen|park|parken|sj[öo]n?|havet|vatten|[äa]ngar|naturreservat|f[äa]lt|gr[öo]nomr[åa]de)',
}
F={k:re.compile(v,re.I) for k,v in F.items()}
def sents(t):
    for line in t.split('\n'):
        for s in re.split(r'(?<=[.!?])\s+',line.strip()):
            s=re.sub(r'\s+',' ',s).strip()
            if 6<=len(s.split())<=60:yield s
led={r['school_id']:r for r in csv.DictReader(open(HERE.parent/'county_progress_20261103_after_step3b.csv'))}
recs={}
for f in [SR/'collection.jsonl',SR/'followup/collection.jsonl',HERE/'collection.jsonl']:
    for l in open(f):
        d=json.loads(l);ok=[(f.parent,p) for p in d['pages'] if p.get('http_status')==200 and p.get('text_file')]
        if ok:recs[d['school_id']]=ok   # later file overrides
out=[]
for sid,pages in recs.items():
    toks=name_tokens(led[sid]['official_directory_name'])
    for base,p in pages:
        title=fold(p.get('page_title') or '')
        if p['label']=='registered' and len(pages)>1 and not any(t in title for t in toks):continue
        txt=(base/p['text_file']).read_text(errors='ignore')
        seen=set()
        for s in sents(txt):
            for k,rx in F.items():
                if rx.search(s) and (k,s) not in seen:
                    seen.add((k,s));out.append(dict(school_id=sid,school=led[sid]['official_directory_name'],feature=k,source_url=p['source_url'],page_title=p.get('page_title'),accessed_date=p.get('accessed_date'),quoted_text=s))
json.dump(out,open(HERE/'candidates.json','w'),ensure_ascii=False,indent=0)
import collections
print(len(recs),'schools with pages;',len(out),'candidates')
print(collections.Counter(o['feature'] for o in out))
print(collections.Counter(o['feature'] for o in {(o['school_id'],o['feature']):o for o in out}.values()))
