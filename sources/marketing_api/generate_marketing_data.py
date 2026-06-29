import json
import os
import random
from datetime import date, timedelta
from faker import Faker
from pymongo import MongoClient
 
fake = Faker("es_ES")   # Spanish locale to match the Spain-heavy campaign data
random.seed(42)
 

 
# ─── Shared constants ─────────────────────────────────────────────────────────
START_DATE     = date(2026, 1, 1)
END_DATE       = date(2026, 3, 31)   # 90 days
DATE_RANGE     = [START_DATE + timedelta(days=i) for i in range((END_DATE - START_DATE).days + 1)]
 
PLATFORMS      = ["Google Ads", "Meta Ads", "TikTok Ads", "LinkedIn Ads", "Pinterest Ads"]
COUNTRIES      = ["Spain", "France", "Germany", "Italy", "Netherlands", "Portugal", "Poland"]
DEVICES        = ["Mobile", "Desktop", "Tablet"]
OBJECTIVES     = ["Awareness", "Consideration", "Conversion", "Retargeting"]
 
CATEGORIES     = ["Electronics", "Clothing", "Home & Garden", "Sports", "Beauty", "Books", "Toys"]
CAMPAIGN_NAMES = {
    "Electronics": ["Winter Tech Sale", "Spring Gadgets", "Mobile Upgrade", "Gaming Season"],
    "Clothing":    ["Summer Fashion", "Back to School", "Winter Collection", "Streetwear Drop"],
    "Home & Garden": ["Spring Refresh", "Home Makeover", "Garden Season", "Interior Trends"],
    "Sports":      ["New Year Fitness", "Summer Sports", "Marathon Season", "Gym Starter"],
    "Beauty":      ["Skincare Essentials", "Beauty Trends", "Glow Up Campaign", "Natural Beauty"],
    "Books":       ["Reading Month", "Educational Push", "Bestsellers Promo", "Kindle Deal"],
    "Toys":        ["Toy Season", "Kids Learning", "Holiday Gifts", "Back to Play"],
}
 
# ─────────────────────────────────────────────────────────────────────────────
# SOURCE A — MARKETING API DATA
# ─────────────────────────────────────────────────────────────────────────────
 
def generate_campaign_metrics(campaign_id, platform, category, name, country, device, objective, spend_budget):
    """
    Derives all downstream metrics from spend so ratios stay realistic.
    Industry benchmarks used:
      CTR:  0.5% – 5%   (TikTok highest, LinkedIn lowest)
      CVR:  1%   – 8%   (Retargeting highest, Awareness lowest)
      CPC:  varies by platform
      CPM:  varies by platform
    """
    platform_ctr = {
        "Google Ads": (0.03, 0.06),
        "Meta Ads":   (0.02, 0.05),
        "TikTok Ads": (0.04, 0.08),
        "LinkedIn Ads": (0.005, 0.02),
        "Pinterest Ads": (0.01, 0.03),
    }
    objective_cvr = {
        "Awareness":     (0.005, 0.015),
        "Consideration": (0.02,  0.04),
        "Conversion":    (0.04,  0.08),
        "Retargeting":   (0.07,  0.14),
    }
    platform_cpm = {
        "Google Ads":    (8,  18),
        "Meta Ads":      (6,  14),
        "TikTok Ads":    (4,  10),
        "LinkedIn Ads":  (25, 55),
        "Pinterest Ads": (5,  12),
    }
 
    cpm_range  = platform_cpm[platform]
    cpm        = round(random.uniform(*cpm_range), 2)
    impressions = int((spend_budget / cpm) * 1000)
 
    ctr_range  = platform_ctr[platform]
    ctr        = random.uniform(*ctr_range)
    clicks     = int(impressions * ctr)
 
    cvr_range    = objective_cvr[objective]
    cvr          = random.uniform(*cvr_range)
    conversions  = int(clicks * cvr)
 
    # Revenue = conversions × avg order value (varies by category)
    aov_by_category = {
        "Electronics":   (150, 600),
        "Clothing":      (40,  120),
        "Home & Garden": (60,  250),
        "Sports":        (50,  200),
        "Beauty":        (25,  80),
        "Books":         (12,  40),
        "Toys":          (20,  90),
    }
    aov     = round(random.uniform(*aov_by_category[category]), 2)
    revenue = round(conversions * aov, 2)
 
    roas           = round(revenue / spend_budget, 2) if spend_budget else 0
    roi_pct        = round(((revenue - spend_budget) / spend_budget) * 100, 1) if spend_budget else 0
    cpc            = round(spend_budget / clicks, 4) if clicks else 0
    cost_per_conv  = round(spend_budget / conversions, 2) if conversions else 0
    ctr_pct        = round(ctr * 100, 3)
    cvr_pct        = round(cvr * 100, 3)
 
    return {
        "campaign_id":          campaign_id,
        "campaign_name":        name,
        "platform":             platform,
        "category":             category,
        "objective":            objective,
        "country":              country,
        "device":               device,
        "spend":                round(spend_budget, 2),
        "impressions":          impressions,
        "clicks":               clicks,
        "conversions":          conversions,
        "revenue":              revenue,
        "cpc":                  cpc,
        "cpm":                  cpm,
        "ctr_pct":              ctr_pct,
        "cvr_pct":              cvr_pct,
        "roas":                 roas,
        "roi_pct":              roi_pct,
        "cost_per_conversion":  cost_per_conv,
        "avg_order_value":      aov,
    }
 
 
def generate_marketing_data():
    print("Generating marketing data...")
 
    NUM_CAMPAIGNS = 40
    campaigns     = []
    ad_spend_rows = []
    clicks_rows   = []
 
    for i in range(1, NUM_CAMPAIGNS + 1):
        cid        = f"CMP{i:03d}"
        platform   = random.choice(PLATFORMS)
        category   = random.choice(CATEGORIES)
        name       = random.choice(CAMPAIGN_NAMES[category])
        country    = random.choice(COUNTRIES)
        device     = random.choice(DEVICES)
        objective  = random.choice(OBJECTIVES)
        budget     = round(random.uniform(500, 15000), 2)
        start      = random.choice(DATE_RANGE[:60])
        duration   = random.randint(7, 30)
        end        = min(start + timedelta(days=duration), END_DATE)
        status     = "active" if end >= END_DATE else "completed"
 
        campaigns.append({
            "campaign_id":    cid,
            "campaign_name":  name,
            "platform":       platform,
            "category":       category,
            "objective":      objective,
            "country":        country,
            "device":         device,
            "total_budget":   budget,
            "start_date":     str(start),
            "end_date":       str(end),
            "status":         status,
        })
 
        # Daily ad_spend & clicks rows for this campaign's date range
        num_days = (end - start).days + 1
        for d in (start + timedelta(days=j) for j in range(num_days)):
            daily_spend  = round(budget / num_days * random.uniform(0.7, 1.3), 2)
            daily_metrics = generate_campaign_metrics(
                cid, platform, category, name, country, device, objective, daily_spend
            )
            daily_metrics["date"] = str(d)
 
            ad_spend_rows.append({
                "campaign_id":         cid,
                "date":                str(d),
                "platform":            platform,
                "country":             country,
                "device":              device,
                "spend":               daily_metrics["spend"],
                "impressions":         daily_metrics["impressions"],
                "clicks":              daily_metrics["clicks"],
                "conversions":         daily_metrics["conversions"],
                "revenue":             daily_metrics["revenue"],
                "cpc":                 daily_metrics["cpc"],
                "cpm":                 daily_metrics["cpm"],
                "roas":                daily_metrics["roas"],
                "roi_pct":             daily_metrics["roi_pct"],
                "cost_per_conversion": daily_metrics["cost_per_conversion"],
            })
 
            clicks_rows.append({
                "campaign_id":  cid,
                "date":         str(d),
                "platform":     platform,
                "country":      country,
                "device":       device,
                "clicks":       daily_metrics["clicks"],
                "impressions":  daily_metrics["impressions"],
                "ctr_pct":      daily_metrics["ctr_pct"],
                "cvr_pct":      daily_metrics["cvr_pct"],
                "conversions":  daily_metrics["conversions"],
            })

 
    print(f"  ✓ {len(campaigns)} campaigns")
    print(f"  ✓ {len(ad_spend_rows)} daily ad_spend rows")
    print(f"  ✓ {len(clicks_rows)} daily clicks rows")
    save_to_mongodb(campaigns,ad_spend_rows,clicks_rows)

def save_to_mongodb(campaigns,ad_spent,clicks):
    
    try:

        mongodb_url = os.getenv("MONGODB_URL","mongodb://localhost:27017/")
        client = MongoClient(mongodb_url)
        db = client["marketing_db"]

        db.campaign.drop()
        db.ad_spend.drop()
        db.clicks.drop()

        db.campaign.insert_many(campaigns)
        db.ad_spend.insert_many(ad_spent)
        db.clicks.insert_many(clicks)

        # Create indexes for query performance
        db.campaigns.create_index("campaign_id", unique=True)
        db.ad_spend.create_index([("campaign_id", 1), ("date", 1)])
        db.clicks.create_index([("campaign_id", 1), ("date", 1)])
 
        client.close()
        print("  ✓ Saved to MongoDB (marketing_db)")
        print("    Collections: campaigns, ad_spend, clicks")
        print("    Indexes created on campaign_id and date")
    except Exception as e:
        print(f"Error saving to mongodb:{e}")

def main():
    generate_marketing_data()

if __name__ == "__main__":
    main()
    