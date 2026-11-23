-- Gold: county medians per metric and the school year they describe (used as reference lines).
select
    metric_key,
    any_value(county_median) as county_median,
    max(period) filter (where value_status in ('reported','estimate')) as latest_period,
    count(value) as schools_with_value
from {{ ref('fct_school_metrics') }}
group by 1
