-- Gold: reviewed teaching-approach claims, one row per school and category, with the quote behind it.
-- These are what a school says about itself on its own website, not verified practice.
select
    school_id,
    category,
    category_short,
    subcategory,
    coding_level,
    quoted_text,
    source_url,
    accessed_date
from {{ ref('stg_approach_codes') }}
