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
        logging.FileHandler("clean_order_items.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_order_items(df, output_dir):
    logger.info("Starting clean_order_items transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
        df = df[df["quantity"] > 0]
        
    if "unit_price" in df.columns:
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
        df = df[df["unit_price"] >= 0]
        
    logger.debug(f"Shape after transformations: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "order_items.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/order_items.parquet"
    output_dir = "data/silver/postgres"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_parquet(input_path)
        clean_order_items(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing order_items: {e}", exc_info=True)
