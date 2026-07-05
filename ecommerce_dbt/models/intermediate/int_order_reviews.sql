select
    r.review_id,
    r.order_id,
    r.review_score,
    r.review_creation_date,
    o.customer_id,
    o.order_purchase_timestamp
from {{ ref('stg_reviews') }} r
join {{ ref('stg_orders') }} o on r.order_id = o.order_id
