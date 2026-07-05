# ETL Pipeline (Extract, Transform, Load)

The project implements an ELT/ETL hybrid architecture. Raw extraction and initial cleaning occur locally before data is bulk-loaded into the cloud warehouse (Snowflake) for heavy SQL-based transformation (via dbt).

## Storage Layers (Local Data Lake)

The ETL process utilizes the host filesystem, mapped via Docker volumes, to store intermediate data state.

* **Bronze (`data/bronze/`)**: 
  - Represents raw data exactly as extracted from the source systems.
  - Postgres extracts are stored as `.parquet` files for efficiency.
  - MongoDB extracts are stored as `.json` files to preserve document structures.
  
* **Silver (`data/silver/`)**: 
  - Cleaned, deduplicated, and strongly-typed data.
  - All data (both Postgres and MongoDB origins) is unified into `.parquet` format at this stage.

## Extraction Tools
- **Postgres**: Extracted via `pandas.read_sql` using an SQLAlchemy engine connecting to the `db` Docker container.
- **MongoDB**: Extracted via `pymongo.MongoClient` and converted to pandas DataFrames. The MongoDB `_id` ObjectIDs are stripped to prevent serialization issues in later stages.

## Transformation Approach (Airflow + Pandas)

While standalone PySpark scripts exist in `etl/transform/`, the orchestrated Airflow DAG (`ecommerce_etl_pipeline.py`) relies entirely on **Pandas**. 

**Why Pandas instead of PySpark?**
Running PySpark requires a JVM and Spark environment, which isn't present in the standard lightweight Apache Airflow Docker image. For the scale of data processed in this platform, Pandas offers a fast, memory-efficient alternative that runs natively inside the Airflow worker processes.

**Common Transformations Applied:**
- **Timestamp Parsing**: Converting strings to `datetime64[ns]` objects (e.g., `order_purchase_timestamp`, `start_date`).
- **Timezone Stripping**: Snowflake's `write_pandas` requires tz-naive timestamps, so `dt.tz_convert(None)` is applied during the load phase.
- **Type Casting**: Ensuring financial metrics (prices, budgets, spend) are stored as standard `float` (Double) types.
- **Null Handling & Deduplication**: Replacing null prices with `0.0`, dropping duplicate `order_id`s, and filtering out invalid `order_status` records.
- **Derived Metrics**: Calculating basic metrics prior to warehousing (e.g., computing `ctr_calculated` from `clicks` and `impressions`).

## Snowflake Loading Layer
The `load_snowflake` task uses the official Snowflake Python Connector and its `write_pandas` utility function.
- It automatically creates target tables in the `RAW` schema (`auto_create_table=True`).
- It forces all column names to uppercase prior to load, complying with Snowflake's default case-insensitivity behavior and preventing downstream quoting issues in dbt.
- Data is overwritten entirely (`overwrite=True`) on each daily run.
