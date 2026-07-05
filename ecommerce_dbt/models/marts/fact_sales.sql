select
  order_id,
  order_item_id,
  product_id,
  customer_id,
  try_to_timestamp(order_purchase_timestamp) as order_timestamp,
  try_to_timestamp(order_purchase_timestamp)::date as order_date,
  price,
  freight_value,
  order_status
from {{ ref('int_order_items_enriched') }}
