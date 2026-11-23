"""Nearby green/water share from OpenStreetMap (Overpass mirror), radius R around Skolverket visiting-address coordinates."""
import json,time,urllib.request,urllib.parse,sys,os
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union,polygonize,transform
from pyproj import Transformer
EP='https://maps.mail.ru/osm/tools/overpass/api/interpreter'
R=int(os.environ.get('R','300'))
T=Transformer.from_crs(4326,3006,always_xy=True).transform
GREEN={'landuse':'forest|meadow|grass|recreation_ground|village_green','natural':'wood|scrub|heath|wetland|grassland','leisure':'park|nature_reserve|garden'}
WATER={'natural':'water'}
def q(pts):
    parts=[]
    for k,v in list(GREEN.items())+list(WATER.items()):
        for lat,lon in pts:
            parts.append(f'way["{k}"~"^({v})$"](around:{R},{lat},{lon});relation["{k}"~"^({v})$"](around:{R},{lat},{lon});')
    return f'[out:json][timeout:300];({"".join(parts)});out geom;'
def kind(tags):
    for k,v in WATER.items():
        if tags.get(k) in v.split('|'):return 'water'
    return 'green'
def geom(e):
    if e['type']=='way':
        c=[T(p['lon'],p['lat']) for p in e.get('geometry',[])]
        return Polygon(c).buffer(0) if len(c)>=4 and c[0]==c[-1] else None
    lines=[LineString([T(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('role')=='outer' and m.get('geometry') and len(m['geometry'])>1]
    inner=[LineString([T(p['lon'],p['lat']) for p in m['geometry']]) for m in e.get('members',[]) if m.get('role')=='inner' and m.get('geometry') and len(m['geometry'])>1]
    o=unary_union(list(polygonize(lines))) if lines else None
    if o is None or o.is_empty:return None
    i=unary_union(list(polygonize(inner))) if inner else None
    return o.difference(i) if i is not None and not i.is_empty else o
reg=[json.loads(l) for l in open('register.jsonl')]
pts={}
for r in reg:
    a=r['resp'].get('data',{}).get('attributes',{}) if isinstance(r['resp'],dict) else {}
    for ad in a.get('addresses',[]):
        g=ad.get('geoCoordinates')
        if ad.get('type')=='BESOKSADRESS' and g and g.get('latitude'):pts[r['sid']]=(float(g['latitude']),float(g['longitude']))
done=set()
out_f=f'nature_r{R}.jsonl'
if os.path.exists(out_f):done={json.loads(l)['sid'] for l in open(out_f)}
todo=[s for s in pts if s not in done]
if len(sys.argv)>1:todo=todo[:int(sys.argv[1])]
B=25
with open(out_f,'a') as f:
    for i in range(0,len(todo),B):
        chunk=todo[i:i+B]
        for a in range(4):
            try:
                data=urllib.parse.urlencode({'data':q([pts[s] for s in chunk])}).encode()
                els=json.load(urllib.request.urlopen(urllib.request.Request(EP,data=data,headers={'User-Agent':'school-approach-review/1.0'}),timeout=400))['elements'];break
            except Exception as e:
                print('retry',e,flush=True);time.sleep(10*2**a)
        else: raise SystemExit('overpass failed')
        G=[(kind(e.get('tags',{})),geom(e),e.get('tags',{}).get('name')) for e in els]
        G=[g for g in G if g[1] is not None and not g[1].is_empty]
        for s in chunk:
            lat,lon=pts[s];p=Point(T(lon,lat));c=p.buffer(R)
            res={'sid':s,'lat':lat,'lon':lon,'radius_m':R}
            for k in ['green','water']:
                gs=[g for kk,g,n in G if kk==k and g.intersects(c)]
                u=unary_union([g.intersection(c) for g in gs]) if gs else None
                res[k+'_share']=round(u.area/c.area,3) if u else 0.0
                near=[(g.distance(p),n) for kk,g,n in G if kk==k and g.distance(p)<=R and g.area>=10000]
                res[k+'_nearest_1ha_m']=round(min(near)[0]) if near else None
                res[k+'_names']=sorted({n for d,n in near if n})[:5]
            f.write(json.dumps(res,ensure_ascii=False)+'\n');f.flush()
        print(i+len(chunk),'/',len(todo),flush=True);time.sleep(5)
