with source as (
    select * from {{ source('raw_ecommerce', 'products') }}
),

renamed as (
    select
        PRODUCT_ID::varchar                                           as product_id,
        coalesce(PRODUCT_CATEGORY_NAME::varchar, 'unknown')           as product_category_name,
        coalesce(try_to_number(PRODUCT_WEIGHT_G::varchar), 0)         as product_weight_g,
        coalesce(try_to_number(PRODUCT_LENGTH_CM::varchar), 0)        as product_length_cm,
        coalesce(try_to_number(PRODUCT_HEIGHT_CM::varchar), 0)        as product_height_cm,
        coalesce(try_to_number(PRODUCT_WIDTH_CM::varchar), 0)         as product_width_cm
    from source
)

select * from renamed
