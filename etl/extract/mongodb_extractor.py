import pandas as pd
import os
from pymongo import MongoClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

def extract_collections(collection_name):
    client = MongoClient(MONGODB_URL)
    db = client["marketing_db"]
    collection = db[collection_name]

    # Efficient: cursor → list → DataFrame (no double JSON serialization)
    df = pd.DataFrame(list(collection.find()))

    # Correct _id column name (single underscore)
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    client.close()  # Prevent connection leaks
    return df

print("Starting MongoDB extraction...")

df_campaigns = extract_collections("campaign")
df_ad_spend = extract_collections("ad_spend")      # Fixed typo
df_clicks = extract_collections("clicks")           # Fixed typo

# Save to bronze layer as JSON
output_dir = "data/bronze/mongodb"
os.makedirs(output_dir, exist_ok=True)

df_campaigns.to_json(f"{output_dir}/campaigns.json", orient="records", indent=2)
df_ad_spend.to_json(f"{output_dir}/ad_spend.json", orient="records", indent=2)
df_clicks.to_json(f"{output_dir}/clicks.json", orient="records", indent=2)

print(f"✅ Saved {len(df_campaigns)} campaigns, {len(df_ad_spend)} ad_spend, {len(df_clicks)} clicks")