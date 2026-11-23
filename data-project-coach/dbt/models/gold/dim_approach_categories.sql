-- Gold: the seven codebook categories with the short names and descriptions parents see.
select c.category, c.short_name, c.description, c.sort_order,
       count(distinct a.school_id) as schools
from {{ ref('approach_categories') }} c
left join {{ ref('school_approach') }} a using (category)
group by all
order by sort_order
