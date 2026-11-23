-- Gold: one row per school and metric with the value a parent sees.
-- Rule: the latest school year that has values county-wide; if the school has no value that year,
-- fall back one year. Never further. The county median is the median of school values (no ranking).
with stats as (
    select st.* from {{ ref('stg_statistics') }} st
    semi join {{ ref('stg_schools') }} sc using (school_id)
),
latest as (
    select metric_key, max(period) as latest_period
    from stats where value is not null
    group by 1
),
candidates as (
    select s.*, l.latest_period, (s.period = l.latest_period) as is_latest
    from stats s join latest l using (metric_key)
    where s.period = l.latest_period or s.period = {{ prev_period('l.latest_period') }}
),
picked as (
    select *
    from candidates
    qualify row_number() over (
        partition by school_id, metric_key
        order by (value is not null) desc, is_latest desc
    ) = 1
),
single as (
    select
        school_id, metric_key,
        value,
        case when value is null then latest_period else period end as period,
        case when value is null then value_status
             when not is_latest then 'reported_previous_year'
             else value_status end as value_status
    from picked
),
-- Combined national test result for year 6 and year 9: mean of maths, Swedish and English
-- when at least two of the three are available.
combined as (
    select
        school_id,
        'np' || right(metric_key, 1)                 as metric_key,
        case when count(value) >= 2 then round(avg(value), 1) end as value,
        coalesce(max(period) filter (where value is not null), max(period)) as period,
        case when count(value) >= 2 then 'reported' else 'not_reported' end as value_status
    from single
    where metric_key in ('ma6', 'sv6', 'en6', 'ma9', 'sv9', 'en9')
    group by school_id, right(metric_key, 1)
),
all_metrics as (
    select * from single
    union all
    select * from combined
),
medians as (
    select metric_key, round(median(value), 1) as county_median, count(value) as schools_with_value
    from all_metrics group by 1
)
select
    a.school_id,
    a.metric_key,
    a.value,
    a.period,
    a.value_status,
    m.county_median,
    case when a.value is null then null
         when a.value > m.county_median then 'above'
         when a.value < m.county_median then 'below'
         else 'equal' end as vs_county
from all_metrics a
join medians m using (metric_key)
