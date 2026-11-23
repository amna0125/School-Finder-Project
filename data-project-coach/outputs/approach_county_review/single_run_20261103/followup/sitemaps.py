import sys,json,re,gzip
sys.path.insert(0,'..')
import fetch
from fetch import get,fold
HOSTS={'0114':'www.upplandsvasby.se','0115':'www.vallentuna.se','0117':'www.osteraker.se','0120':'www.varmdo.se','0123':'www.jarfalla.se','0125':'www.ekero.se','0126':'www.huddinge.se','0127':'www.botkyrka.se','0136':'www.haninge.se','0138':'www.tyreso.se','0139':'www.upplands-bro.se','0140':'nykvarn.se','0160':'www.taby.se','0162':'www.danderyd.se','0163':'www.sollentuna.se','0180':'grundskola.stockholm','0181':'www.sodertalje.se','0182':'www.nacka.se','0183':'www.sundbyberg.se','0186':'lidingo.se','0187':'www.vaxholm.se','0188':'www.norrtalje.se','0191':'www.sigtuna.se','0192':'nynashamn.se'}
def locs(url,depth=0,acc=None):
    acc=acc if acc is not None else []
    if depth>2 or len(acc)>200000:return acc
    r=get(url)
    if r.get('http_status')!=200:return acc
    b=r['content']
    if url.endswith('.gz'):
        try:b=gzip.decompress(b)
        except:pass
    t=b.decode('utf-8','ignore')
    L=re.findall(r'<loc>\s*([^<\s]+)\s*</loc>',t)
    if '<sitemapindex' in t:
        for u in L:locs(u,depth+1,acc)
    else:acc+=L
    return acc
out={}
for code,h in HOSTS.items():
    base='https://'+h
    rp,info=fetch.robots(base+'/')
    sms=[]
    r=get(base+'/robots.txt')
    if r.get('http_status')==200:sms=re.findall(r'(?im)^sitemap:\s*(\S+)',r['content'].decode('utf-8','ignore'))
    if not sms:sms=[base+'/sitemap.xml']
    acc=[]
    for s in sms:locs(s,0,acc)
    out[code]=sorted(set(acc));print(code,h,len(out[code]),flush=True)
json.dump(out,open('sitemaps.json','w'))
