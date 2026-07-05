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
        logging.FileHandler("clean_reviews.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_reviews(df, output_dir):
    logger.info("Starting clean_reviews transformation...")
    logger.debug(f"Initial shape: {df.shape}")

    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        # Keep only valid ratings between 1 and 5
        df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]
        
    if "review_text" in df.columns:
        df["review_text"] = df["review_text"].str.strip()
        df["review_text"] = df["review_text"].fillna("")
        
    logger.debug(f"Shape after transformations: {df.shape}")

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "reviews.parquet")
    df.to_parquet(output_path, index=False)
    logger.info(f"Successfully saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/reviews.parquet"
    output_dir = "data/silver/postgres"
    
    logger.info(f"Reading data from {input_path}")
    try:
        df = pd.read_parquet(input_path)
        clean_reviews(df, output_dir)
    except Exception as e:
        logger.error(f"Error processing reviews: {e}", exc_info=True)
