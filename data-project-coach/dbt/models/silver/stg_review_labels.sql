-- Silver: the manual review outcome per school (from the review ledger seed).
select school_id, review_state, batch_reference
from {{ ref('review_labels') }}
