"""Amna 2026-11-10: one card feature 'Green surroundings' = 300 m map band (+ share) with the school's nearby-nature claim as a quote under it. 500 m shares stored, hidden."""
import json,duckdb
from pathlib import Path
H=Path(__file__).resolve().parent
c=duckdb.connect('/home/user/proj/.state/schools.duckdb')
c.execute("delete from School_setting where feature='green_space_500m'")
src='https://geodata.naturvardsverket.se/geoserver/wms (lc-nmd:LC.LandCoverRaster.Bas.2023.v2.x)'
for l in open(H/'nmd_r500.jsonl'):
    x=json.loads(l);v=round(x.get('forest',0)+x.get('open_green',0),3)
    c.execute("insert into School_setting(school_id,feature,value,numeric_value,source_type,scope,source_url,accessed_date,method_note) values (?,?,?,?,?,?,?,?,?)",
      [x['sid'],'green_space_500m',None,v,'Naturvårdsverket land-cover map','map, 500 m radius',src,x['retrieved_at'][:10],'Green share in 500 m circle; 2026-11-10 test, not shown on card (79% of schools keep the same band as at 300 m).'])
c.execute("update School_setting set method_note=method_note||' Shown on the card as the quote under Green surroundings (decision 2026-11-10).' where feature='nature_nearby_stated' and method_note not like '%Green surroundings%'")
spec=json.loads((H/'card_spec.json').read_text())
spec['show']=[f for f in spec['show'] if f!='green_space_300m']
spec['show'].insert(1,'green_surroundings = green_space_300m band + share, with nature_nearby_stated quote under it when the school makes one')
spec['show'].insert(2,'food_cooked_on_site')
spec['hidden_kept_in_db']=['forest_300m','water_300m','green_space_500m']
spec['pending']=[];spec['decided']='2026-11-09/10 with Amna'
(H/'card_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=1))
print(spec);print(c.execute("select feature,count(*) from School_setting group by 1 order by 1").fetchall())
