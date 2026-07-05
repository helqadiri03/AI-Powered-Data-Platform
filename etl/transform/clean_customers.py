import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lower, trim, when

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_customers.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_customers(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_customers transformation...")
    
    df = spark.read.parquet(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "email" in df.columns:
        df = df.withColumn("email", lower(trim(col("email"))))
        
    if "registration_date" in df.columns:
        df = df.withColumn("registration_date", to_timestamp(col("registration_date")))
        
    for c in ["first_name", "last_name"]:
        if c in df.columns:
            df = df.withColumn(c, when(col(c).isNull(), "Unknown").otherwise(col(c)))

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "customers.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/customers.parquet"
    output_dir = "data/silver/postgres"
    
    spark = SparkSession.builder \
        .appName("CleanCustomers") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_customers(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing customers: {e}", exc_info=True)
    finally:
        spark.stop()
