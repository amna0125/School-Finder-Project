-- Gold: one wide row per school. This is what the finder filters and scores in the browser.
with m as (
    select
        school_id,
        {% for k in ['teachers','merit9','np6','np9','pass9','pass6','ptr','elig'] %}
        max(value) filter (where metric_key = '{{ k }}')        as {{ k }},
        max(value_status) filter (where metric_key = '{{ k }}') as {{ k }}_status,
        {% endfor %}
        max(period) filter (where metric_key = 'teachers')      as teachers_period
    from {{ ref('fct_school_metrics') }}
    group by 1
),
ap as (
    select school_id,
           list(distinct category order by category) as approach_categories,
           count(*)                                    as approach_codes
    from {{ ref('school_approach') }}
    group by 1
),
green as (
    select school_id, value as green_level, green_pct
    from {{ ref('school_setting') }} where feature = 'green_space_300m'
),
fritids as (
    select school_id, value as fritidshem
    from {{ ref('school_setting') }} where feature = 'fritidshem_registered'
),
happy as (
    select school_id, positive_pct as parents_satisfied_pct
    from {{ ref('school_survey') }}
    where respondent_group = 'parents' and theme_key = 'sat'
)
select
    s.school_id,
    s.school_name,
    s.municipality_name,
    s.address,
    -- Coordinates outside the county are source errors: the school stays in the list, but not on the map.
    case when s.latitude_raw between 58.6 and 60.4 and s.longitude_raw between 17.0 and 19.6 then s.latitude_raw end  as latitude,
    case when s.latitude_raw between 58.6 and 60.4 and s.longitude_raw between 17.0 and 19.6 then s.longitude_raw end as longitude,
    s.organizer_type,
    s.organizer_name,
    s.grades,
    s.grades_label,
    s.website,
    l.review_state,
    coalesce(ap.approach_categories, []::varchar[]) as approach_categories,
    coalesce(ap.approach_codes, 0)                  as approach_codes,
    green.green_level,
    green.green_pct,
    fritids.fritidshem,
    happy.parents_satisfied_pct,
    m.* exclude (school_id)
from {{ ref('stg_schools') }} s
left join {{ ref('stg_review_labels') }} l using (school_id)
left join m using (school_id)
left join ap using (school_id)
left join green using (school_id)
left join fritids using (school_id)
left join happy using (school_id)
