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
        logging.FileHandler("clean_clicks.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_clicks(df, output_dir):
    logger.info("Starting clean_clicks transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "click_timestamp" in df.columns:
        df["click_timestamp"] = pd.to_datetime(df["click_timestamp"], errors="coerce")
        initial_len = len(df)
        df.dropna(subset=["click_timestamp"], inplace=True)
        logger.info(f"Dropped {initial_len - len(df)} rows due to missing click_timestamp.")
        
    # Ensure user_id and session_id are strings
    for col in ["user_id", "session_id", "ad_id"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
        
    logger.debug(f"Shape after transformations: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "clicks.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/clicks.json"
    output_dir = "data/silver/mongodb"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_json(input_path)
        clean_clicks(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing clicks: {e}", exc_info=True)
