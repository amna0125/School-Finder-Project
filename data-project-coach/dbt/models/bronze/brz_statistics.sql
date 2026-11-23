-- Bronze: raw statistics as loaded, no changes.
select * from {{ source('raw', 'statistics') }}
