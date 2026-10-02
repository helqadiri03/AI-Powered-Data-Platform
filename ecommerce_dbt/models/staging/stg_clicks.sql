with source as (
    select * from {{ source('raw_ecommerce', 'clicks') }}
),

renamed as (
    select
        CAMPAIGN_ID::varchar                                         as campaign_id,
        try_to_timestamp(DATE::varchar)::date                        as date,
        coalesce(try_to_number(CLICKS::varchar)::bigint, 0)          as clicks,
        coalesce(try_to_number(IMPRESSIONS::varchar)::bigint, 0)     as impressions,
        coalesce(try_to_number(CONVERSIONS::varchar)::bigint, 0)     as conversions
    from source
)

select * from renamed
