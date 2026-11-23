-- Silver: Skolverket statistics with the source's symbols translated into a value status.
--   '..'   few pupils, value withheld       -> few_pupils
--   '~100' rounded, few pupils not eligible -> rounded
--   '*'    teachers without legitimation    -> teachers_excluded
--   '.' / empty                             -> not_reported
select
    st.school_unit_code                       as school_id,
    st.metric                                 as source_metric,
    d.metric_key,
    st.period,
    st.raw_value,
    st.numeric_value                          as value,
    case
        when st.numeric_value is not null and st.raw_value ilike 'cirka%' then 'estimate'
        when st.numeric_value is not null                                then 'reported'
        when st.value_type = 'OMITTED_DUE_TO_BASED_ON_FEW_PUPILS'         then 'few_pupils'
        when st.value_type like 'ROUNDED%'                                then 'rounded'
        when st.value_type = 'TEACHERS_EXCLUDED_DUE_TO_NO_REQUIRED_LEGITIMATION' then 'teachers_excluded'
        else 'not_reported'
    end                                       as value_status
from {{ ref('brz_statistics') }} st
join {{ ref('metric_dictionary') }} d on d.source_metric = st.metric
where st.period is not null
