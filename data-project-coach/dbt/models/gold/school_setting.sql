-- Gold: setting features shown on the school page. Green space within 300 m comes from map data;
-- the other features are stated on school websites (with a quote) or taken from the register.
select
    school_id,
    feature,
    value,
    case when feature = 'green_space_300m' then round(numeric_value * 100)::integer end as green_pct,
    quoted_text,
    accessed_date
from {{ ref('stg_school_setting') }}
where feature not in ('forest_300m', 'water_300m', 'green_space_500m')
