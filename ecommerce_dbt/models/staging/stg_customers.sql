with source as (
    select * from {{ source('raw_ecommerce', 'customers') }}
),

renamed as (
    select
        CUSTOMER_ID::varchar          as customer_id,
        CUSTOMER_UNIQUE_ID::varchar   as customer_unique_id,
        lower(trim(CUSTOMER_CITY::varchar))  as customer_city,
        upper(trim(CUSTOMER_STATE::varchar)) as customer_state,
        CUSTOMER_ZIP_CODE_PREFIX::varchar    as customer_zip_code_prefix
    from source
)

select * from renamed
