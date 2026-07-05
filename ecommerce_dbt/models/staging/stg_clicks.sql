with source as (
    select * from {{ source('raw_ecommerce', 'clicks') }}
)

select * from source
