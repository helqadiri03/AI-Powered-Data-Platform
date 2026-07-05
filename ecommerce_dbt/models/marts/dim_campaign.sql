select
  campaign_id,
  campaign_name,
  category,
  platform,
  objective,
  status,
  total_budget,
  start_date,
  end_date
from {{ ref('stg_campaigns') }}
