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
        logging.FileHandler("clean_campaigns.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_campaigns(df, output_dir):
    logger.info("Starting clean_campaigns transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    if "end_date" in df.columns:
        df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
        
    if "campaign_budget" in df.columns:
        df["campaign_budget"] = pd.to_numeric(df["campaign_budget"], errors="coerce").fillna(0)
        
    logger.debug(f"Shape after type conversions: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "campaigns.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/campaigns.json"
    output_dir = "data/silver/mongodb"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_json(input_path)
        clean_campaigns(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing campaigns: {e}", exc_info=True)
