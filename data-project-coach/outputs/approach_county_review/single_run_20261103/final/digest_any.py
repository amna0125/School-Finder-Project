"""Print compact review digests (verbatim lines) for given school ids."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).parent
KW=re.compile(r'montessori|waldorf|steiner|reggio|freinet|profil|inriktning|pedagogik|arbetssätt|arbetar vi|förhållningssätt|musik|konst|estetisk|drama|dans|teater|skapande|kreativ|kultur|utomhus|utepedagog|ute|natur|skog|i ur och skur|tvåspråk|bilingual|engelsk|english|international|språk|ib |cambridge|npf|inkluder|anpassning|tillgänglig|lugn|trivsel|hälsa|rörelse|idrott|fotboll|hockey|ridning|nta|tema|projekt|ämnesöver|entreprenör|digital|programmering|teknik|naturvetenskap|matematik|läsning|läs|kiva|pax|relationsinriktad|mindfulness|yoga|hållbar|miljö|kristen|kristna|konfessionell|islam|judisk|katolsk|finska|arabiska|franska|tyska|spanska|tvålärar|mentor|elevinflytande|dansk|norsk',re.I)
def load(sid):
    for l in (Path(sys.argv[1])).open():
        d=json.loads(l)
        if d['school_id']==sid:return d
def digest(sid,budget=2000):
    d=load(sid);out=[f"### {sid} {d['name']} | hint={d['outcome_hint']} | reg={d['registered_url']}"]
    if d['events']:out.append('events: '+json.dumps(d['events'],ensure_ascii=False)[:300])
    seen=set();used=0
    found=any(p['label'].startswith('school_page') for p in d['pages'])
    for i,p in enumerate(d['pages']):
        if found and p['label'].startswith('registered'):out.append(f"[p{i}] (generic registered page skipped) {p['source_url']}");continue
        lines=[l for l in (ROOT/p['text_file']).read_text().split('\n') if len(l)>=25]
        out.append(f"[p{i}] {p['page_title']} <{p['source_url']}>")
        keep=[]
        for j,l in enumerate(lines):
            if l in seen:continue
            seen.add(l)
            if KW.search(l) or j<4:keep.append(l)
        for l in keep:
            if used>budget:break
            s=l if len(l)<450 else l[:450]+' …'
            out.append('  '+s);used+=len(s)
    return '\n'.join(out)
if __name__=='__main__':
    for s in sys.argv[2].split(','):print(digest(s));print()
