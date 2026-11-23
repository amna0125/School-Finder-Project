-- Bronze: raw schools as loaded, no changes.
select * from {{ source('raw', 'schools') }}
