with source as (
    select * from {{ source('raw_ecommerce', 'order_items') }}
),

renamed as (
    select
        ORDER_ID::varchar                               as order_id,
        ORDER_ITEM_ID::int                              as order_item_id,
        PRODUCT_ID::varchar                             as product_id,
        SELLER_ID::varchar                              as seller_id,
        try_to_timestamp(SHIPPING_LIMIT_DATE::varchar)  as shipping_limit_date,
        coalesce(try_to_number(PRICE::varchar), 0)      as price,
        coalesce(try_to_number(FREIGHT_VALUE::varchar), 0) as freight_value
    from source
    where coalesce(try_to_number(PRICE::varchar), 0) >= 0
      and coalesce(try_to_number(FREIGHT_VALUE::varchar), 0) >= 0
)

select * from renamed
