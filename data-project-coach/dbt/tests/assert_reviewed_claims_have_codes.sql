-- Every school labelled "Reviewed claim" has at least one approach code, and no other school has any.
select school_id, review_state, approach_codes
from {{ ref('school_card') }}
where (review_state = 'Reviewed claim' and approach_codes = 0)
   or (review_state <> 'Reviewed claim' and approach_codes > 0)
