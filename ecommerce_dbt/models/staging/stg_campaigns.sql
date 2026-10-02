with source as (
    select * from {{ source('raw_ecommerce', 'campaigns') }}
),

renamed as (
    select
        CAMPAIGN_ID::varchar                               as campaign_id,
        CAMPAIGN_NAME::varchar                             as campaign_name,
        CATEGORY::varchar                                  as category,
        PLATFORM::varchar                                  as platform,
        OBJECTIVE::varchar                                 as objective,
        STATUS::varchar                                    as status,
        coalesce(try_to_number(TOTAL_BUDGET::varchar), 0)  as total_budget,
        try_to_timestamp(START_DATE::varchar)::date        as start_date,
        try_to_timestamp(END_DATE::varchar)::date          as end_date
    from source
)

select * from renamed
