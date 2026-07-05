with source as (
    select * from {{ source('raw_ecommerce', 'reviews') }}
)

select * from source
