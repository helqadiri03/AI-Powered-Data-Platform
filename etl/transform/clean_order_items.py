import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_order_items.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_order_items(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_order_items transformation...")
    
    df = spark.read.parquet(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "quantity" in df.columns:
        df = df.withColumn("quantity", col("quantity").cast("double"))
        df = df.fillna({"quantity": 0.0})
        df = df.filter(col("quantity") > 0)
        
    if "unit_price" in df.columns:
        df = df.withColumn("unit_price", col("unit_price").cast("double"))
        df = df.fillna({"unit_price": 0.0})
        df = df.filter(col("unit_price") >= 0)

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "order_items.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/order_items.parquet"
    output_dir = "data/silver/postgres"
    
    spark = SparkSession.builder \
        .appName("CleanOrderItems") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_order_items(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing order_items: {e}", exc_info=True)
    finally:
        spark.stop()
