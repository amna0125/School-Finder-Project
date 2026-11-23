"""Build School_setting table (long format) from: Skolverket register (fritidshem), NMD 2023 land cover around coordinates, reviewed website quotes."""
import json,csv,duckdb,statistics as st,collections
from pathlib import Path
H=Path(__file__).resolve().parent
reg={json.loads(l)['sid']:json.loads(l) for l in open(H/'register.jsonl')}
nmd={json.loads(l)['sid']:json.loads(l) for l in open(H/'nmd_r300.jsonl')}
web=json.load(open(H/'web_features.json'))
rows=[]
def add(**k):
    base=dict(school_id=None,feature=None,value=None,numeric_value=None,source_type=None,scope=None,source_url=None,page_title=None,quoted_text=None,accessed_date=None,method_note=None)
    base.update(k);rows.append(base)
for s,r in reg.items():
    a=r['resp']['data']['attributes']
    add(school_id=s,feature='fritidshem_registered',value='yes' if 'FTH' in a.get('schoolTypes',[]) else 'not at this school unit',source_type='Skolverket school register',scope='official register',source_url=f'https://api.skolverket.se/skolenhetsregistret/v2/school-units/{s}',accessed_date=r['retrieved_at'][:10],method_note='schoolTypes contains FTH (fritidshem). "not at this school unit" can mean fritids is registered under another unit.')
g={s:x.get('forest',0)+x.get('open_green',0) for s,x in nmd.items()}
q=st.quantiles(list(g.values()),n=4)
for s,x in nmd.items():
    v=g[s];band='much green space' if v>=q[2] else ('little green space' if v<q[0] else 'some green space')
    note=f'Share of 300 m circle around Skolverket visiting-address coordinate classed as forest, wetland, shrub or grass in NMD 2023 (10 m). County quartiles: {q[0]:.2f}/{q[1]:.2f}/{q[2]:.2f}. Bands relative to Stockholm county; land cover, not schoolyard.'
    src='https://geodata.naturvardsverket.se/geoserver/wms (lc-nmd:LC.LandCoverRaster.Bas.2023.v2.x)'
    add(school_id=s,feature='green_space_300m',value=band,numeric_value=round(v,3),source_type='Naturvårdsverket land-cover map',scope='map, 300 m radius',source_url=src,accessed_date=x['retrieved_at'][:10],method_note=note)
    add(school_id=s,feature='forest_300m',value=None,numeric_value=x.get('forest',0),source_type='Naturvårdsverket land-cover map',scope='map, 300 m radius',source_url=src,accessed_date=x['retrieved_at'][:10],method_note='Forest share of 300 m circle (NMD 2023).')
    w=x.get('water',0)
    add(school_id=s,feature='water_300m',value='yes' if w>=0.05 else 'no',numeric_value=w,source_type='Naturvårdsverket land-cover map',scope='map, 300 m radius',source_url=src,accessed_date=x['retrieved_at'][:10],method_note='Lake or sea covers at least 5% of the 300 m circle.')
for w in web:
    add(school_id=w['school_id'],feature=w['feature'],value=w['value'],source_type=w['source_type'],scope=w['scope'],source_url=w['source_url'],page_title=w['page_title'],quoted_text=w['quoted_text'],accessed_date=w['accessed_date'],method_note='Pattern match on saved public pages, then manual check; quote is a school claim, not verified. Not mentioned = unknown.')
db='/home/user/proj/.state/schools.duckdb'
c=duckdb.connect(db)
c.execute('create or replace table School_setting(school_id varchar, feature varchar, value varchar, numeric_value double, source_type varchar, scope varchar, source_url varchar, page_title varchar, quoted_text varchar, accessed_date varchar, method_note varchar)')
c.executemany('insert into School_setting values (?,?,?,?,?,?,?,?,?,?,?)',[tuple(r.values()) for r in rows])
print(c.execute('select feature,value,count(*) from School_setting group by all order by 1,2').fetchall())
print('quartiles',q)
