import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, initcap, when

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_products.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_products(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_products transformation...")
    
    df = spark.read.parquet(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "price" in df.columns:
        df = df.withColumn("price", col("price").cast("double"))
        df = df.fillna({"price": 0.0})
        df = df.filter(col("price") >= 0)
        
    if "category" in df.columns:
        df = df.withColumn("category", initcap(trim(col("category"))))
        df = df.withColumn("category", when(col("category").isNull(), "Uncategorized").otherwise(col("category")))

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "products.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/products.parquet"
    output_dir = "data/silver/postgres"
    
    spark = SparkSession.builder \
        .appName("CleanProducts") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_products(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing products: {e}", exc_info=True)
    finally:
        spark.stop()
