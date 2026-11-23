-- Bronze: raw Approach_codes as loaded, no changes.
select * from {{ source('raw', 'Approach_codes') }}
