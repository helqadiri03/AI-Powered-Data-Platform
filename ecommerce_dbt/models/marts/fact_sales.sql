select
  order_id,
  order_item_id,
  product_id,
  customer_id,
  order_purchase_timestamp as order_timestamp,
  order_purchase_timestamp::date as order_date,
  price,
  freight_value,
  order_status
from {{ ref('int_order_items_enriched') }}
