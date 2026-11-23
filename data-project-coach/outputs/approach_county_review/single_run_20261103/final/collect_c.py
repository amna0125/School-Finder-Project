import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent))
import fetch
fetch.SRC=HERE/'sources';fetch.SRC.mkdir(exist_ok=True)
T={'65487837':('Futuraskolan International Stockholm','https://futuraskolan.se/schools/stockholm/'),
'39130058':('Montessoriskolan Vigelsjö','https://www.montessoriskolan.nu/'),
'13954336':('Resursskolan vid Martinskolan','https://martinskolan.se/resursskola'),
'34672217':('Älta resursskola','https://www.nacka.se/valfard-skola/alta-resursskola/om-oss/'),
'10311303':('Lilla Kulturama','http://www.kulturama.se'),
'40467992':('Futuraskolan International Hertig Karl','https://futuraskolan.se/schools/hertig-karl/'),
'40978257':('Futuraskolan International School of Stockholm','https://futuraskolaninternational.se/')}
with open(HERE/'collection_c.jsonl','w') as f:
    for s,(n,u) in T.items():
        r=fetch.collect(dict(school_id=s,official_directory_name=n,registered_url=u))
        f.write(json.dumps(r,ensure_ascii=False)+'\n');print(s,n,r['outcome_hint'],[(p['label'],p['source_url'],p['http_status']) for p in r['pages']],flush=True)
