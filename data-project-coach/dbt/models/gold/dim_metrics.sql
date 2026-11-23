-- Gold: metric labels and units for the website, with the county median.
select d.metric_key, d.label, d.unit, d.year_group, c.county_median, c.latest_period
from {{ ref('metric_dictionary') }} d
left join {{ ref('county_medians') }} c using (metric_key)
union all
select k, l, 'test points', y, c.county_median, c.latest_period
from (values ('np6', 'National tests, year 6 (maths, Swedish, English)', 6),
             ('np9', 'National tests, year 9 (maths, Swedish, English)', 9)) v(k, l, y)
left join {{ ref('county_medians') }} c on c.metric_key = v.k
