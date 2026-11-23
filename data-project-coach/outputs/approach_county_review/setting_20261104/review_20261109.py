"""Apply Amna's School setting review decisions (2026-11-09, Claude Doc 'School setting review'). Idempotent on a fresh build_setting.py table."""
import duckdb,re,json
from pathlib import Path
H=Path(__file__).resolve().parent
c=duckdb.connect('/home/user/proj/.state/schools.duckdb')
log={}
# 1 fritidshem: not applicable where the unit has no years F-5 (fritidshem serves pupils up to ~12)
n=c.execute("""update School_setting set value='not applicable (no years F–5 at this unit)', method_note=method_note||' Review 2026-11-09: units without any of years 1–5 marked not applicable.'
 where feature='fritidshem_registered' and value='not at this school unit' and school_id in (select school_unit_code from schools where not regexp_matches(grades_json,'"[1-5]"'))""").fetchone()
log['fritids_na']=c.execute("select count(*) from School_setting where feature='fritidshem_registered' and value like 'not applicable%'").fetchone()[0]
# 2 green space labels relative to county
for a,b in [('much green space','greener than most'),('some green space','typical'),('little green space','less green than most')]:
    c.execute("update School_setting set value=? where feature='green_space_300m' and value=?",[b,a])
# 7 sports hall: keep only a hall at the school itself (manual read of all 80 quotes); drop access to/nearby halls elsewhere
DROP_HALL=['20137688','32965692','34225123','36350546','37416253','38975788','40631085','45104329','45279651','47243834','49631077','52885189','59848694','63682476','77002828','85440729']
log['sports_hall_dropped']=len(DROP_HALL)
c.execute(f"delete from School_setting where feature='facility_sports_hall' and school_id in ({','.join('?'*len(DROP_HALL))})",DROP_HALL)
# 8 arts/science rooms: special rooms only
SPECIAL=r'musiksal|musikstudio|orkestersal|labb|laborator|makerspace|teater|aula|dans|replokal|no-sal|ateljé|atelje|skapanderum'
log['arts_dropped']=c.execute(f"select count(*) from School_setting where feature='facility_arts_or_science_rooms' and not regexp_matches(lower(quoted_text),'{SPECIAL}')").fetchone()[0]
c.execute(f"delete from School_setting where feature='facility_arts_or_science_rooms' and not regexp_matches(lower(quoted_text),'{SPECIAL}')")
# 10 schoolyard: 'green' only when the yard itself is green; nearby-nature phrasing -> large (if described large) or removed, and counted as nearby nature
NEAR=r'n[äa]ra till|n[äa]rhet|i anslutning|intill|granne'
rows=c.execute(f"select * from School_setting where feature='schoolyard_described' and value='green/natural' and regexp_matches(lower(quoted_text),'{NEAR}')").fetchall()
cols=[d[0] for d in c.description];moved=[]
for r in rows:
    d=dict(zip(cols,r))
    big=re.search(r'stor|rymlig|nyrenoverad|upprust',d['quoted_text'].lower())
    if big and d['school_id']!='71078874':c.execute("update School_setting set value='large/renovated/varied' where feature='schoolyard_described' and school_id=?",[d['school_id']])
    else:c.execute("delete from School_setting where feature='schoolyard_described' and school_id=?",[d['school_id']])
    if not c.execute("select 1 from School_setting where feature='nature_nearby_stated' and school_id=?",[d['school_id']]).fetchone():
        d.update(feature='nature_nearby_stated',value='yes');c.execute(f"insert into School_setting values ({','.join('?'*len(cols))})",list(d.values()))
    moved.append((d['school_id'],'large' if big else 'removed'))
log['schoolyard_reclassified']=moved
# card spec: which features the parent card shows
spec=dict(decided='2026-11-09 with Amna',show=['fritidshem_registered','green_space_300m','food_sustainable_or_vegetarian_focus','facility_sports_hall','facility_arts_or_science_rooms','premises_new_or_renovated (show accessed_date)','schoolyard_described'],
 hidden_kept_in_db=['forest_300m','water_300m'],pending=['food_cooked_on_site (Amna questions parent value)','nature_nearby_stated (use as check on map; 500 m test proposed)'],website_blank_means='not stated on pages read')
(H/'card_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=1))
log['counts']=c.execute("select feature,value,count(*) from School_setting group by all order by 1,2").fetchall()
(H/'review_20261109_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=1,default=str))
print(json.dumps(log,ensure_ascii=False,default=str))
