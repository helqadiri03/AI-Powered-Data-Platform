import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_orders.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_orders(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_orders transformation...")
    
    df = spark.read.parquet(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "order_date" in df.columns:
        df = df.withColumn("order_date", to_timestamp(col("order_date")))
        
    if "total_amount" in df.columns:
        df = df.withColumn("total_amount", col("total_amount").cast("double"))
        df = df.fillna({"total_amount": 0.0})
        df = df.filter(col("total_amount") >= 0)
        
    if "order_id" in df.columns:
        df = df.dropDuplicates(["order_id"])

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "orders.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/orders.parquet"
    output_dir = "data/silver/postgres"
    
    spark = SparkSession.builder \
        .appName("CleanOrders") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_orders(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing orders: {e}", exc_info=True)
    finally:
        spark.stop()
