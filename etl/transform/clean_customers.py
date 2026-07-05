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
        logging.FileHandler("clean_customers.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_customers(df, output_dir):
    logger.info("Starting clean_customers transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "email" in df.columns:
        df["email"] = df["email"].str.strip().str.lower()
        
    if "registration_date" in df.columns:
        df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
        
    # Handle missing names
    for col in ["first_name", "last_name"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
            
    logger.debug(f"Shape after transformations: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "customers.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/customers.parquet"
    output_dir = "data/silver/postgres"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_parquet(input_path)
        clean_customers(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing customers: {e}", exc_info=True)
