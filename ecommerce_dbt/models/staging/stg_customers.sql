with source as (
    select * from {{ source('raw_ecommerce', 'customers') }}
)

select * from source
