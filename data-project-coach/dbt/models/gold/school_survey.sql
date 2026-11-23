-- Gold: survey shares per school, respondent group and theme.
-- Shares are re-based on those who answered (100 - no answer). A theme is dropped when fewer than
-- 30 % answered, or when the shown shares add up to less than 95 % of those who answered
-- (the source prints '-' for small shares, which is only safe to read as 0 when the rest adds up).
with g as (
    select
        school_id, respondent_group, theme_key,
        coalesce(sum(share_pct) filter (where answer_group = 'no_answer'), 0) as no_answer,
        coalesce(sum(share_pct) filter (where answer_group = 'pos'), 0) as pos,
        coalesce(sum(share_pct) filter (where answer_group = 'mid'), 0) as mid,
        coalesce(sum(share_pct) filter (where answer_group = 'neg'), 0) as neg,
        max(answers) as answers
    from {{ ref('stg_survey') }}
    group by all
)
select
    school_id, respondent_group, theme_key,
    round(pos / (pos + mid + neg) * 100)::integer as positive_pct,
    round(mid / (pos + mid + neg) * 100)::integer as middle_pct,
    round(neg / (pos + mid + neg) * 100)::integer as negative_pct,
    answers
from g
where 100 - no_answer >= 30
  and pos + mid + neg >= (100 - no_answer) * 0.95
  and pos + mid + neg > 0
