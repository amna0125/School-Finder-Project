-- Bronze: the saved register responses, unpacked only as far as needed.
-- Names, e-mail addresses and phone numbers in the source are deliberately NOT selected.
select
    sid                                                         as school_unit_code,
    retrieved_at,
    resp.data.attributes.displayName                            as display_name,
    resp.data.attributes.schoolName                             as school_name,
    resp.data.attributes.municipalityCode                       as municipality_code,
    resp.data.attributes.url                                    as website,
    resp.data.attributes.schoolTypes                            as school_types,
    resp.data.attributes.schoolTypeProperties.gr.grades         as gr_grades,
    resp.data.attributes.addresses                              as addresses,
    resp.included.attributes.organizerType                      as organizer_type,
    resp.included.attributes.displayName                        as organizer_name
from {{ source('register', 'register_responses') }}
