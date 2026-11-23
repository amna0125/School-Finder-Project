-- Silver: setting features. Map-based features keep their numeric share; stated features keep their quote.
select
    school_id,
    feature,
    value,
    numeric_value,
    source_type,
    scope,
    source_url,
    quoted_text,
    try_cast(accessed_date as date) as accessed_date
from {{ ref('brz_school_setting') }}
