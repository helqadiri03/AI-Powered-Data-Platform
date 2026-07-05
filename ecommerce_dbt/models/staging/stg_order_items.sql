with source as (
    select * from {{ source('raw_ecommerce', 'order_items') }}
)

select * from source
