import os
import logging
import sys
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("snowflake_loader.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        
        db = os.getenv("SNOWFLAKE_DATABASE")
        schema = os.getenv("SNOWFLAKE_SCHEMA")
        
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
        cursor.execute(f"USE DATABASE {db}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        cursor.execute(f"USE SCHEMA {schema}")
        
        logger.info("Successfully connected to Snowflake and set schema.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Snowflake: {e}")
        raise

def load_to_snowflake(conn, dataset_path, table_name):
    logger.info(f"Loading {dataset_path} into Snowflake table {table_name}...")
    try:
        # Read the entire directory of parquet files
        df = pd.read_parquet(dataset_path)
        
        # Snowflake expects uppercase column names generally, so let's uppercase them to avoid quote issues
        df.columns = [col.upper() for col in df.columns]
        
        # Ensure datetimes are timezone naive for Snowflake if required, but pandas usually handles it
        for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
            # Snowflake handles timestamps better if they are timezone naive in Pandas
            if df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_convert(None)

        logger.info(f"Uploading {len(df)} rows to {table_name}...")
        
        # write_pandas handles the staging and COPY INTO natively
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name.upper(),
            auto_create_table=True,
            overwrite=True
        )
        
        if success:
            logger.info(f"Successfully uploaded {nrows} rows to {table_name} in {nchunks} chunks.")
        else:
            logger.error(f"Failed to upload data to {table_name}.")
            
    except Exception as e:
        logger.error(f"Error loading {dataset_path} to {table_name}: {e}", exc_info=True)

def main():
    datasets = [
        {"path": "data/silver/mongodb/ad_spend.parquet", "table": "AD_SPEND"},
        {"path": "data/silver/mongodb/campaigns.parquet", "table": "CAMPAIGNS"},
        {"path": "data/silver/mongodb/clicks.parquet", "table": "CLICKS"},
        {"path": "data/silver/postgres/customers.parquet", "table": "CUSTOMERS"},
        {"path": "data/silver/postgres/order_items.parquet", "table": "ORDER_ITEMS"},
        {"path": "data/silver/postgres/orders.parquet", "table": "ORDERS"},
        {"path": "data/silver/postgres/products.parquet", "table": "PRODUCTS"},
        {"path": "data/silver/postgres/reviews.parquet", "table": "REVIEWS"}
    ]
    
    conn = get_snowflake_connection()
    try:
        for dataset in datasets:
            if os.path.exists(dataset["path"]):
                load_to_snowflake(conn, dataset["path"], dataset["table"])
            else:
                logger.warning(f"Path does not exist, skipping: {dataset['path']}")
    finally:
        conn.close()
        logger.info("Snowflake connection closed.")

if __name__ == "__main__":
    main()
