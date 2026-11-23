-- Silver: one clean row per school unit in the review (762).
with reg as (
    select
        r.*,
        list_filter(r.addresses, lambda a: a.type = 'BESOKSADRESS')[1] as visit
    from {{ ref('brz_register') }} r
),
grades as (
    select
        school_unit_code,
        list_contains(school_types, 'FKLASS') as has_fklass,
        list_transform(list_filter(gr_grades, lambda g: regexp_matches(g, '^[0-9]+$')), lambda g: cast(g as integer)) as gr_int
    from reg
)
select
    s.school_unit_code                                                as school_id,
    coalesce(r.display_name, r.school_name, s.name)                   as school_name,
    s.municipality_code as municipality_code,
    m.municipality_name,
    trim(both ', ' from coalesce(r.visit.streetAddress, '') || ', ' || coalesce(r.visit.locality, '')) as address,
    try_cast(r.visit.geoCoordinates.latitude as double)               as latitude_raw,
    try_cast(r.visit.geoCoordinates.longitude as double)              as longitude_raw,
    case when r.organizer_type = 'KOMMUN' then 'municipal' else 'independent' end as organizer_type,
    r.organizer_name,
    case when g.has_fklass and len(g.gr_int) > 0 then list_prepend(0, g.gr_int) else g.gr_int end as grades,
    case when len(r.gr_grades) > 0
         then (case when g.has_fklass then 'F' else r.gr_grades[1] end) || '–' || r.gr_grades[-1]
         else '' end                                                  as grades_label,
    coalesce(r.website, s.website)                                    as website,
    s.status                                                          as register_status
from {{ ref('brz_schools') }} s
left join reg r using (school_unit_code)
left join grades g using (school_unit_code)
left join {{ ref('municipalities') }} m on m.municipality_code = s.municipality_code
