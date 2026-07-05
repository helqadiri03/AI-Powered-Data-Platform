# Snowflake Configuration

Snowflake serves as the centralized Cloud Data Warehouse for the platform.

## Schemas & Architecture

We utilize two schemas within the primary database (`ECOMMERCE_DB`):

1. **`RAW` Schema**
   - The landing zone for all ETL extracts.
   - Tables map 1:1 with source systems (e.g., `CUSTOMERS`, `ORDERS`, `CAMPAIGNS`).
   - Populated dynamically by Airflow using `write_pandas` (which leverages Snowflake staging and `COPY INTO` natively).

2. **`MARTS` Schema**
   - The highly optimized Star Schema target for our frontend UI and BI tools.
   - Populated entirely by dbt (`ecommerce_dbt`).
   - Contains clean Dimensions (e.g., `DIM_CUSTOMER`) and Facts (e.g., `FACT_SALES`).
   - **Important**: The Text-to-SQL AI Agent is strictly restricted to querying *only* tables within this schema.

## Python Integration

All python-based interactions with Snowflake use the official `snowflake-connector-python` package.

- **FastAPI / Queries**: Uses `DictCursor` to retrieve query results natively as Python dictionaries, mapped straight to JSON responses.
- **Airflow / Loading**: Uses the `write_pandas` utility function for efficient bulk uploading of the Silver layer `.parquet` files.

## Security & Connectivity
- Authentication uses standard username/password flows.
- Credentials are provided via `.env` and injected into the FastAPI runtime via Pydantic `BaseSettings`.
- For dbt, these are injected into the runtime environment and read by `profiles.yml`.
