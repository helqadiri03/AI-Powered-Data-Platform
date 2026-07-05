with source as (
    select * from {{ source('raw_ecommerce', 'campaigns') }}
)

select * from source
