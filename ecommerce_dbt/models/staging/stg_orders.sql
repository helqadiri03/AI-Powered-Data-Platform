with source as (
    select * from {{ source('raw_ecommerce', 'orders') }}
)

select * from source
