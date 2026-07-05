select
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    p.product_category_name,
    oi.price,
    oi.freight_value,
    o.customer_id,
    o.order_purchase_timestamp,
    o.order_status
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
left join {{ ref('stg_products') }} p on oi.product_id = p.product_id
