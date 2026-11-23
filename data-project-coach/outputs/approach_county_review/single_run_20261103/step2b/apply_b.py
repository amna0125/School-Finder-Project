import csv, sys
sys.path.insert(0,'single_run_20261103')
from labels import NOCLEAR, UNCERTAIN, BLOCKED
src='county_progress_20261103_after_step2.csv'; dst='county_progress_20261103_after_step2b.csv'
RULE='Step 2 rule B (agreed with Amna): another unit\'s approach on a shared page is not applied to the registered school'
N_ids={'95676943','46239244','26804905','15080815','17287315','16068461'}
U_ids={'19353396','15331669','22513261','24561769'}
B_ids={'94279206'}
rows=list(csv.DictReader(open(src))); f=list(rows[0].keys()); n=0
for r in rows:
    s=r['school_id']
    if s not in N_ids|U_ids|B_ids: continue
    assert r['review_state']==UNCERTAIN, s
    old=r['note']
    if s in N_ids:
        r.update(review_state=NOCLEAR, flag_for_joint_review='no', flag_reason='', note=f'{RULE}; nothing on the page is stated for the registered school itself. | Earlier: {old}')
    elif s in U_ids:
        r.update(flag_reason='isolated / generic claim', note=f'{RULE}; the school\'s own weak claim moved to step 3. | Earlier: {old}')
    else:
        r.update(review_state=BLOCKED, flag_reason='school-specific source not found', note=f'{RULE}; only the host school\'s page exists, the resource school has no page of its own. | Earlier: {old}')
    r['batch_reference']='single_run_20261103/step2b'; n+=1
assert n==11
w=csv.DictWriter(open(dst,'w',newline=''),fieldnames=f); w.writeheader(); w.writerows(rows)
from collections import Counter; print(Counter(r['review_state'] for r in rows))
