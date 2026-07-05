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
        logging.FileHandler("clean_orders.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_orders(df, output_dir):
    logger.info("Starting clean_orders transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        
    if "total_amount" in df.columns:
        df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
        df = df[df["total_amount"] >= 0]
        
    if "order_id" in df.columns:
        initial_len = len(df)
        df.drop_duplicates(subset=["order_id"], inplace=True)
        logger.info(f"Dropped {initial_len - len(df)} duplicate orders.")
        
    logger.debug(f"Shape after transformations: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "orders.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/orders.parquet"
    output_dir = "data/silver/postgres"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_parquet(input_path)
        clean_orders(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing orders: {e}", exc_info=True)
