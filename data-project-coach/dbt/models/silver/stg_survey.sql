-- Silver: VT26 survey answer shares (percent) for the five themes, grouped into positive / middle / negative.
-- Respondent group is 'parents', or the pupils' year group ('ak5', 'ak8').
select
    o.school_unit_code                                         as school_id,
    case when o.respondent = 'parents' then 'parents' else o.year_group end as respondent_group,
    t.theme_key,
    o.question,
    o.measure,
    g.answer_group,
    o.numeric_value                                            as share_pct,
    o.raw_value,
    try_cast(o.answers_raw as integer)                         as answers
from {{ ref('brz_survey_observations') }} o
join {{ ref('survey_themes') }} t on t.source_metric = o.metric
join {{ ref('survey_answer_groups') }} g on g.measure = o.measure
where o.semester = 'VT26' and o.unit = 'percent'
