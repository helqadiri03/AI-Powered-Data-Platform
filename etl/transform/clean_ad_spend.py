import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, when, lit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_ad_spend.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_ad_spend(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_ad_spend transformation...")
    
    # Read JSON
    df = spark.read.option("multiline", "true").json(input_path)
    logger.info(f"Initial row count: {df.count()}")

    numeric_cols = ["spend","impressions","clicks","conversions","revenue","cpc","cpm","roas","roi_pct","cost_per_conversion"]
    
    # Type Conversion & Null Handling
    for c in numeric_cols:
        if c in df.columns:
            df = df.withColumn(c, col(c).cast("double"))
            df = df.fillna({c: 0.0})
            
    if "date" in df.columns:
        df = df.withColumn("date", to_timestamp(col("date")))
        df = df.dropna(subset=["date"])

    # Business Rule Validation
    if "spend" in df.columns:
        df = df.filter(col("spend") > 0)
        
    if "clicks" in df.columns and "impressions" in df.columns:
        df = df.withColumn(
            "ctr_calculated", 
            when(col("impressions") > 0, col("clicks") / col("impressions")).otherwise(None)
        )
        df = df.withColumn(
            "ctr_calculated",
            when((col("ctr_calculated") > 1) | (col("ctr_calculated") < 0), lit(None)).otherwise(col("ctr_calculated"))
        )

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ad_spend.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    # Need to read it back to get exact count as writing triggers the actions
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/mongodb/ad_spend.json"
    output_dir = "data/silver/mongodb"
    
    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("CleanAdSpend") \
        .master("local[*]") \
        .getOrCreate()
        
    # Reduce Spark logging verbosity
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_ad_spend(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing ad_spend: {e}", exc_info=True)
    finally:
        spark.stop()
