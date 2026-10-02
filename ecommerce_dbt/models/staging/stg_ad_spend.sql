with source as (
    select * from {{ source('raw_ecommerce', 'ad_spend') }}
),

renamed as (
    select
        CAMPAIGN_ID::varchar                                         as campaign_id,
        to_timestamp_ntz(AD_DATE::varchar)::date                     as date,
        coalesce(try_to_number(SPEND::varchar, 18, 4), 0)            as spend,
        coalesce(try_to_number(IMPRESSIONS::varchar)::bigint, 0)     as impressions,
        coalesce(try_to_number(CLICKS::varchar)::bigint, 0)          as clicks,
        coalesce(try_to_number(CONVERSIONS::varchar)::bigint, 0)     as conversions,
        coalesce(try_to_number(REVENUE::varchar, 18, 4), 0)          as revenue,
        -- Derived metric: click-through rate (dbt owns this logic in ELT)
        div0(
            try_to_number(CLICKS::varchar),
            try_to_number(IMPRESSIONS::varchar)
        )                                                            as ctr_calculated
    from source
    where to_timestamp_ntz(AD_DATE::varchar) is not null
      and coalesce(try_to_number(SPEND::varchar, 18, 4), 0) > 0
)

select * from renamed
