with source as (
    select * from {{ source('raw_ecommerce', 'products') }}
)

select * from source
