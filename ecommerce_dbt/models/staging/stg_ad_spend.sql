with source as (
    select * from {{ source('raw_ecommerce', 'ad_spend') }}
)

select * from source
