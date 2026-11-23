-- Bronze: raw School_setting as loaded, no changes.
select * from {{ source('raw', 'School_setting') }}
