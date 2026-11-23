"""Land cover share within R m of each school's Skolverket visiting-address coordinate, from Naturvårdsverket NMD 2023 (WMS, 10 m)."""
import json,time,urllib.request,io,os
from PIL import Image
R=int(os.environ.get('R','300'));PX=10
L='lc-nmd:LC.LandCoverRaster.Bas.2023.v2.x'
leg=json.load(open('nmd_legend.json'))
col={}
for r in leg['Legend'][0]['rules']:
    for s in r['symbolizers']:
        for e in s.get('Raster',{}).get('colormap',{}).get('entries',[]):
            c=e['color'].lstrip('#');col[tuple(int(c[i:i+2],16) for i in (0,2,4))]=int(float(e['quantity']))
def grp(q):
    if q in (61,62):return 'water'
    if q in (23,43) or 111<=q<=128 :return 'forest'
    if 200<=q<=228 or 4211<=q<=4233:return 'open_green'
    if q==3:return 'farmland'
    if q in (51,52,53,411,54):return 'built'
    return 'other'
pts={}
for l in open('register.jsonl'):
    r=json.loads(l);a=r['resp'].get('data',{}).get('attributes',{}) if isinstance(r['resp'],dict) else {}
    for ad in a.get('addresses',[]):
        g=ad.get('geoCoordinates')
        if ad.get('type')=='BESOKSADRESS' and g and g.get('coordinateSweRefE'):pts[r['sid']]=(float(g['coordinateSweRefE'].replace(',','.')),float(g['coordinateSweRefN'].replace(',','.')))
out=f'nmd_r{R}.jsonl';done={json.loads(l)['sid'] for l in open(out)} if os.path.exists(out) else set()
n=2*R//PX
with open(out,'a') as f:
    for s,(E,N) in pts.items():
        if s in done:continue
        u=f'https://geodata.naturvardsverket.se/geoserver/wms?service=WMS&version=1.1.1&request=GetMap&layers={L}&styles=&srs=EPSG:3006&bbox={E-R},{N-R},{E+R},{N+R}&width={n}&height={n}&format=image/png'
        for a in range(4):
            try:im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'school-approach-review/1.0'}),timeout=60).read())).convert('RGBA');break
            except Exception as e:print('retry',s,e,flush=True);time.sleep(3*2**a)
        else:continue
        cnt={};unk=0;tot=0
        for y in range(n):
            for x in range(n):
                if ((x+.5-n/2)**2+(y+.5-n/2)**2)*PX*PX>R*R:continue
                p=im.getpixel((x,y));tot+=1
                if p[3]==0:cnt['nodata']=cnt.get('nodata',0)+1;continue
                q=col.get(p[:3])
                g=grp(q) if q is not None else 'unmatched'
                cnt[g]=cnt.get(g,0)+1
        f.write(json.dumps({'sid':s,'E':E,'N':N,'radius_m':R,'source':'NMD 2023 bas v2 (Naturvårdsverket WMS)','retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**{k:round(v/tot,3) for k,v in cnt.items()}})+'\n');f.flush()
        time.sleep(0.2)
