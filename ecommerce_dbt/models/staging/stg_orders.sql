with source as (
    select * from {{ source('raw_ecommerce', 'orders') }}
),

renamed as (
    select
        ORDER_ID::varchar                                      as order_id,
        CUSTOMER_ID::varchar                                   as customer_id,
        ORDER_STATUS::varchar                                  as order_status,
        try_to_timestamp(ORDER_PURCHASE_TIMESTAMP::varchar)    as order_purchase_timestamp,
        try_to_timestamp(ORDER_APPROVED_AT::varchar)           as order_approved_at,
        try_to_timestamp(ORDER_DELIVERED_CARRIER_DATE::varchar) as order_delivered_carrier_date,
        try_to_timestamp(ORDER_DELIVERED_CUSTOMER_DATE::varchar) as order_delivered_customer_date,
        try_to_timestamp(ORDER_ESTIMATED_DELIVERY_DATE::varchar) as order_estimated_delivery_date
    from source
    where ORDER_STATUS is not null
      and ORDER_ID is not null
    qualify row_number() over (partition by ORDER_ID order by ORDER_PURCHASE_TIMESTAMP) = 1
)

select * from renamed
