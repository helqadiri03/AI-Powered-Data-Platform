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
        logging.FileHandler("clean_campaigns.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_campaigns(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_campaigns transformation...")
    
    df = spark.read.option("multiline", "true").json(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "start_date" in df.columns:
        df = df.withColumn("start_date", to_timestamp(col("start_date")))
    if "end_date" in df.columns:
        df = df.withColumn("end_date", to_timestamp(col("end_date")))
        
    if "campaign_budget" in df.columns:
        df = df.withColumn("campaign_budget", col("campaign_budget").cast("double"))
        df = df.fillna({"campaign_budget": 0.0})

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "campaigns.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/campaigns.json"
    output_dir = "data/silver/mongodb"
    
    spark = SparkSession.builder \
        .appName("CleanCampaigns") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_campaigns(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing campaigns: {e}", exc_info=True)
    finally:
        spark.stop()
