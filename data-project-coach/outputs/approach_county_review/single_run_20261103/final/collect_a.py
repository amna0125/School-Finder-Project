import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
import fetch
fetch.SRC=HERE/'sources';fetch.SRC.mkdir(exist_ok=True)
T={'43238662':('Björkhaga Skola','http://www.botkyrka.se/bjorkhagaskola'),'67742754':('Karsby International School','http://www.botkyrka.se/karsbyinternationalschool'),
'75580959':('Rikstens skola','http://www.botkyrka.se/rikstensskola'),'45757947':('Tallidsskolan','http://www.botkyrka.se/tallidsskolan'),
'41357379':('Skogsbacksskolan Trampolinen','https://www.botkyrka.se/skola-och-forskola/grundskola/hitta-grundskola-och-ansok/grundskolor-i-botkyrka/skogsbacksskolan'),
'75527289':('Västerhaninge Montessoriskola','http://www.ugglan.net'),'33922950':('Smedslättsskolan','https://grundskola.stockholm/hitta-grundskola/grundskola/smedslattsskolan')}
with open(HERE/'collection_a.jsonl','w') as f:
    for s,(n,u) in T.items():
        r=fetch.collect(dict(school_id=s,official_directory_name=n,registered_url=u))
        f.write(json.dumps(r,ensure_ascii=False)+'\n');print(s,n,r['outcome_hint'],[(p['label'],p['source_url'],p['http_status']) for p in r['pages']],flush=True)
