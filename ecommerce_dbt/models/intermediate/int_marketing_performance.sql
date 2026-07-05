select
    c.campaign_id,
    c.campaign_name,
    c.category,
    c.platform,
    to_timestamp_ntz(a.date, 9)::date as performance_date,
    a.spend,
    a.impressions,
    cl.clicks,
    cl.conversions,
    a.revenue
from {{ ref('stg_campaigns') }} c
join {{ ref('stg_ad_spend') }} a on c.campaign_id = a.campaign_id
join {{ ref('stg_clicks') }} cl on c.campaign_id = cl.campaign_id and to_timestamp_ntz(a.date, 9)::date = cl.date::date
