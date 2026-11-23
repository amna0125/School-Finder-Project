import csv,json,time,urllib.request,os
ids=[r['school_id'] for r in csv.DictReader(open('../county_progress_20261103_after_step3b.csv'))]
out=open('register.jsonl','a'); done={json.loads(l)['sid'] for l in open('register.jsonl')} if os.path.getsize('register.jsonl') else set()
for s in ids:
    if s in done: continue
    for a in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.skolverket.se/skolenhetsregistret/v2/school-units/{s}',headers={'User-Agent':'school-approach-review/1.0'}),timeout=30));break
        except Exception as e: d={'error':str(e)}; time.sleep(2**a)
    out.write(json.dumps({'sid':s,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'resp':d},ensure_ascii=False)+'\n'); out.flush(); time.sleep(0.3)
