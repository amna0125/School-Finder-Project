"""Wide export of School_setting, one row per school (same columns as school_setting_20261104.csv)."""
import duckdb,csv,sys
out=sys.argv[1]
c=duckdb.connect('/home/user/proj/.state/schools.duckdb',read_only=True)
names=dict(c.execute("select school_unit_code,name from schools").fetchall())
rows={}
for s,f,v,n,q in c.execute("select school_id,feature,value,numeric_value,quoted_text from School_setting").fetchall():
    r=rows.setdefault(s,{'school_id':s,'school':names.get(s)})
    if f=='green_space_300m':r[f]=v;r['green_space_share_300m']=n
    elif f=='green_space_500m':r['green_space_share_500m']=n
    elif f=='forest_300m':r['forest_share_300m']=n
    elif f=='water_300m':r[f]=v;r['water_share_300m']=n
    else:
        r[f]=v
        if q:r[f+'_quote']=q
cols=open('school_setting_20261104.csv',encoding='utf-8-sig').readline().strip().split(',');cols.insert(cols.index('green_space_share_300m')+1,'green_space_share_500m')
with open(out,'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=cols);w.writeheader()
    for s in sorted(rows):w.writerow({k:rows[s].get(k,'') for k in cols})
print(len(rows))
