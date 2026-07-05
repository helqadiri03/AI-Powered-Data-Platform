import os
import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, when

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("clean_reviews.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def clean_reviews(spark, input_path, output_dir):
    logger.info("Starting PySpark clean_reviews transformation...")
    
    df = spark.read.parquet(input_path)
    logger.info(f"Initial row count: {df.count()}")

    if "rating" in df.columns:
        df = df.withColumn("rating", col("rating").cast("double"))
        df = df.filter((col("rating") >= 1) & (col("rating") <= 5))
        
    if "review_text" in df.columns:
        df = df.withColumn("review_text", trim(col("review_text")))
        df = df.withColumn("review_text", when(col("review_text").isNull(), "").otherwise(col("review_text")))

    # Save to parquet
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "reviews.parquet")
    df.write.mode("overwrite").parquet(output_path)
    
    final_count = spark.read.parquet(output_path).count()
    logger.info(f"Successfully saved {final_count} rows to {output_path}")

if __name__ == "__main__":
    input_path = "data/bronze/postgres/reviews.parquet"
    output_dir = "data/silver/postgres"
    
    spark = SparkSession.builder \
        .appName("CleanReviews") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        clean_reviews(spark, input_path, output_dir)
    except Exception as e:
        logger.error(f"Error processing reviews: {e}", exc_info=True)
    finally:
        spark.stop()
