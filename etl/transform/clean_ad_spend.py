import pandas as pd
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_ad_spend.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_ad_spend(df, output_dir):
    logger.info("Starting clean_ad_spend transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    ## Step 2: Type Conversion (The Foundation)
    numeric_cols = ["spend","impressions","clicks","conversions","revenue","cpc","cpm","roas","roi_pct","cost_per_conversion"]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    logger.debug("Completed type conversions.")

    ## Step 3: Handling Missing Values Strategically
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    if "date" in df.columns:
        initial_len = len(df)
        df.dropna(subset=["date"], inplace=True)
        logger.info(f"Dropped {initial_len - len(df)} rows due to missing dates.")

    ## Step 4: Business Rule Validation
    if "spend" in df.columns:
        df = df[df["spend"] > 0]
        logger.debug(f"Shape after filtering spend > 0: {df.shape}")
        
    if "clicks" in df.columns and "impressions" in df.columns:
        df["ctr_calculated"] = df["clicks"] / df["impressions"].replace(0, float("nan"))
        invalid_ctr = (df["ctr_calculated"] > 1) | (df["ctr_calculated"] < 0)
        df.loc[invalid_ctr, "ctr_calculated"] = None
        logger.debug("Calculated CTR and nullified invalid ones.")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ad_spend.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/ad_spend.json"
    output_dir = "data/silver/mongodb"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_json(input_path)
        clean_ad_spend(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing ad_spend: {e}", exc_info=True)
