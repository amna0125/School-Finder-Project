-- The county review covers exactly 762 school units.
select count(*) as n from {{ ref('school_card') }} having count(*) <> 762
