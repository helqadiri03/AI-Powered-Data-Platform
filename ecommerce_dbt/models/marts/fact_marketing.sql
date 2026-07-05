select
  campaign_id,
  performance_date,
  platform,
  spend,
  impressions,
  clicks,
  conversions,
  revenue
from {{ ref('int_marketing_performance') }}
