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
        logging.FileHandler("clean_clicks.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_clicks(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_clicks transformation...")
    
    df = spark.read.option("multiline", "true").json(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "click_timestamp" in df.columns:
        df = df.withColumn("click_timestamp", to_timestamp(col("click_timestamp")))
        df = df.dropna(subset=["click_timestamp"])
        
    for c in ["user_id", "session_id", "ad_id"]:
        if c in df.columns:
            df = df.withColumn(c, col(c).cast("string"))

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "clicks.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/clicks.json"
    output_dir = "data/silver/mongodb"
    
    spark = SparkSession.builder \
        .appName("CleanClicks") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_clicks(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing clicks: {e}", exc_info=True)
    finally:
        spark.stop()
