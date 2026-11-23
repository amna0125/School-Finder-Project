-- Bronze: raw Approach_evidence as loaded, no changes.
select * from {{ source('raw', 'Approach_evidence') }}
