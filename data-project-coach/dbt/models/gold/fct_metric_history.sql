-- Gold: all reported school years for the trend lines (teachers, merit rating, passed all subjects,
-- combined national tests). A series needs at least two years.
with base as (
    select s.school_id, s.metric_key, s.period, s.value
    from {{ ref('stg_statistics') }} s
    join {{ ref('metric_dictionary') }} d using (metric_key)
    where d.keep_history and s.value is not null
),
combined as (
    select school_id, 'np' || right(metric_key, 1) as metric_key, period, round(avg(value), 1) as value
    from base
    where metric_key in ('ma6', 'sv6', 'en6', 'ma9', 'sv9', 'en9')
    group by school_id, right(metric_key, 1), period
    having count(*) >= 2
),
series as (
    select * from base where metric_key in ('teachers', 'merit9', 'pass9')
    union all
    select * from combined
)
select *
from series
qualify count(*) over (partition by school_id, metric_key) >= 2
