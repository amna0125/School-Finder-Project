"""Standard review_state labels (Amna approved normalisation on 2026-11-03)."""
REVIEWED='Reviewed claim'
UNCERTAIN='Uncertain evidence - requires review'
NOCLEAR='No clear evidence in scoped review'
BLOCKED='Blocked - requires review'
PENDING='Not yet reviewed'
NOPAGE='No usable public page'  # final outcome agreed with Amna 2026-11-04 (joint review step 4)
LABELS=[REVIEWED,UNCERTAIN,NOCLEAR,BLOCKED,NOPAGE,PENDING]
FLAGGED={UNCERTAIN,BLOCKED}
# per-school overrides decided from batch01 follow-up context (no codes loaded)
PRIOR_OVERRIDES={
 '10035236':(NOCLEAR,''),'10225038':(NOCLEAR,''),'10230535':(NOCLEAR,''),'10998117':(NOCLEAR,''),
 '10311303':(BLOCKED,'unit identity'),'10735290':(BLOCKED,'school-specific source not found'),
 '12407147':(BLOCKED,'school-specific source not found'),'11364996':(UNCERTAIN,'dated / aspirational claim')}
def normalise(sid,old,has_codes):
    o=old.lower().replace('_',' ')
    if o.startswith('prior contextual') or o.startswith('prior pilot'):
        if has_codes: return REVIEWED,('scope caveats remain' if 'pilot' in o else 'follow-ups may remain')
        return PRIOR_OVERRIDES[sid]
    if 'not yet' in o: return PENDING,''
    if 'reviewed' in o and 'claim' in o: return REVIEWED,''
    if 'no clear' in o: return NOCLEAR,''
    if 'permission' in o: return BLOCKED,'permission / terms'+(' + unit identity' if 'identity' in o else '')
    if 'identity' in o: return BLOCKED,'unit identity'
    if 'dormant' in o: return BLOCKED,'dormant status'
    if 'inaccessible' in o: return BLOCKED,'source inaccessible'
    if 'uncertain' in o or 'unclear' in o: return UNCERTAIN,''
    raise ValueError(old)
