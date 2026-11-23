-- Silver: reviewed approach codes joined to their quoted evidence.
select
    c.code_id,
    c.school_id,
    c.category,
    cat.short_name                                   as category_short,
    c.subcategory,
    case c.coding_level when 'Explicit' then 'E' else 'S' end as coding_level,
    c.confidence,
    c.review_status,
    e.evidence_id,
    e.quoted_text,
    e.source_url,
    e.page_title,
    cast(e.accessed_date as date)                    as accessed_date
from {{ ref('brz_approach_codes') }} c
join {{ ref('brz_approach_evidence') }} e using (evidence_id)
join {{ ref('approach_categories') }} cat using (category)
