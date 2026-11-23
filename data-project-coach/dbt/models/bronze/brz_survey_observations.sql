-- Bronze: raw survey_observations as loaded, no changes.
select * from {{ source('raw', 'survey_observations') }}
