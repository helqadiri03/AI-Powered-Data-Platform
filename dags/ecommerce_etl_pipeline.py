"""
ecommerce_etl_pipeline DAG
===========================
Full end-to-end pipeline:

  extract_postgres  ─┐
                     ├─► transform_orders ──┐
  extract_mongodb  ──┘                      ├─► transform_products ──► load_snowflake ──► dbt_build
                     └─► (marketing data)  ─┘

Task breakdown:
  1. extract_postgres   – Reads all tables from PostgreSQL → data/bronze/postgres/*.parquet
  2. extract_mongodb    – Reads campaigns/ad_spend/clicks from MongoDB → data/bronze/mongodb/*.json
  3. transform_orders   – Cleans orders + order_items (pandas) → data/silver/postgres/
  4. transform_products – Cleans products, customers, reviews, campaigns, ad_spend, clicks
                         → data/silver/postgres/ & data/silver/mongodb/
  5. load_snowflake     – Uploads all silver-layer parquets to Snowflake RAW schema
  6. dbt_build          – Runs `dbt build` to materialise STAGING → INTERMEDIATE → MARTS

Schedule: daily at 02:00 UTC
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# ---------------------------------------------------------------------------
# Default args
# ---------------------------------------------------------------------------
DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ---------------------------------------------------------------------------
# Path constants  (relative to project root mounted into Airflow at /opt/airflow)
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/opt/airflow"
BRONZE_PG   = f"{PROJECT_ROOT}/data/bronze/postgres"
BRONZE_MDB  = f"{PROJECT_ROOT}/data/bronze/mongodb"
SILVER_PG   = f"{PROJECT_ROOT}/data/silver/postgres"
SILVER_MDB  = f"{PROJECT_ROOT}/data/silver/mongodb"
DBT_PROJECT = f"{PROJECT_ROOT}/ecommerce_dbt"


# ===========================================================================
# Task 1 — extract_postgres
# ===========================================================================
def extract_postgres() -> None:
    """Extract all relational tables from PostgreSQL into bronze parquet files."""
    from sqlalchemy import create_engine

    log = logging.getLogger("extract_postgres")
    os.makedirs(BRONZE_PG, exist_ok=True)

    pg_host = os.getenv("POSTGRES_HOST", "db")
    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    pg_db   = os.getenv("POSTGRES_DB", "ai_powered_eco_db")

    engine = create_engine(f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}/{pg_db}")

    tables = {
        "customers":   "SELECT * FROM customers",
        "orders":      "SELECT * FROM orders",
        "order_items": "SELECT * FROM order_items",
        "products":    "SELECT * FROM products",
        "reviews":     "SELECT * FROM reviews",
    }

    for table, query in tables.items():
        log.info("Extracting table: %s", table)
        df = pd.read_sql(query, engine)
        out = f"{BRONZE_PG}/{table}.parquet"
        df.to_parquet(out, index=False)
        log.info("Saved %d rows → %s", len(df), out)

    log.info("PostgreSQL extraction complete.")


# ===========================================================================
# Task 2 — extract_mongodb
# ===========================================================================
def extract_mongodb() -> None:
    """Extract marketing collections from MongoDB into bronze JSON files."""
    from pymongo import MongoClient

    log = logging.getLogger("extract_mongodb")
    os.makedirs(BRONZE_MDB, exist_ok=True)

    mongo_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/")
    client = MongoClient(mongo_url)
    db = client["marketing_db"]

    collections = {
        "campaigns": "campaign",
        "ad_spend":  "ad_spend",
        "clicks":    "clicks",
    }

    for filename, col_name in collections.items():
        log.info("Extracting collection: %s", col_name)
        docs = list(db[col_name].find())
        df = pd.DataFrame(docs)
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)
        out = f"{BRONZE_MDB}/{filename}.json"
        df.to_json(out, orient="records", indent=2)
        log.info("Saved %d records → %s", len(df), out)

    client.close()
    log.info("MongoDB extraction complete.")


# ===========================================================================
# Task 3 — transform_orders
# ===========================================================================
def transform_orders() -> None:
    """Clean and validate orders + order_items from bronze into silver."""
    log = logging.getLogger("transform_orders")
    os.makedirs(SILVER_PG, exist_ok=True)

    # ---- orders ----
    log.info("Cleaning orders…")
    orders = pd.read_parquet(f"{BRONZE_PG}/orders.parquet")

    ts_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in ts_cols:
        if col in orders.columns:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")

    orders = orders.drop_duplicates(subset=["order_id"])
    orders = orders[orders["order_status"].notna()]
    orders.to_parquet(f"{SILVER_PG}/orders.parquet", index=False)
    log.info("Orders: %d rows saved.", len(orders))

    # ---- order_items ----
    log.info("Cleaning order_items…")
    items = pd.read_parquet(f"{BRONZE_PG}/order_items.parquet")

    for num_col in ["price", "freight_value"]:
        if num_col in items.columns:
            items[num_col] = pd.to_numeric(items[num_col], errors="coerce").fillna(0.0)
            items = items[items[num_col] >= 0]

    if "shipping_limit_date" in items.columns:
        items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"], errors="coerce")

    items.to_parquet(f"{SILVER_PG}/order_items.parquet", index=False)
    log.info("Order items: %d rows saved.", len(items))


# ===========================================================================
# Task 4 — transform_products
# ===========================================================================
def transform_products() -> None:
    """
    Clean products, customers, reviews (Postgres) and
    campaigns, ad_spend, clicks (MongoDB) into silver parquets.
    """
    log = logging.getLogger("transform_products")
    os.makedirs(SILVER_PG,  exist_ok=True)
    os.makedirs(SILVER_MDB, exist_ok=True)

    # ---- products ----
    log.info("Cleaning products…")
    products = pd.read_parquet(f"{BRONZE_PG}/products.parquet")
    for nc in ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        if nc in products.columns:
            products[nc] = pd.to_numeric(products[nc], errors="coerce").fillna(0.0)
    if "product_category_name" in products.columns:
        products["product_category_name"] = products["product_category_name"].fillna("unknown")
    products.to_parquet(f"{SILVER_PG}/products.parquet", index=False)
    log.info("Products: %d rows saved.", len(products))

    # ---- customers ----
    log.info("Cleaning customers…")
    customers = pd.read_parquet(f"{BRONZE_PG}/customers.parquet")
    customers = customers.drop_duplicates(subset=["customer_id"])
    for sc in ["customer_city", "customer_state"]:
        if sc in customers.columns:
            customers[sc] = customers[sc].str.strip().str.lower()
    customers.to_parquet(f"{SILVER_PG}/customers.parquet", index=False)
    log.info("Customers: %d rows saved.", len(customers))

    # ---- reviews ----
    log.info("Cleaning reviews…")
    reviews = pd.read_parquet(f"{BRONZE_PG}/reviews.parquet")
    if "review_score" in reviews.columns:
        reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
        reviews = reviews[reviews["review_score"].between(1, 5)]
    reviews.to_parquet(f"{SILVER_PG}/reviews.parquet", index=False)
    log.info("Reviews: %d rows saved.", len(reviews))

    # ---- campaigns (MongoDB) ----
    log.info("Cleaning campaigns…")
    campaigns = pd.read_json(f"{BRONZE_MDB}/campaigns.json", orient="records")
    for dc in ["start_date", "end_date"]:
        if dc in campaigns.columns:
            campaigns[dc] = pd.to_datetime(campaigns[dc], errors="coerce")
    if "total_budget" in campaigns.columns:
        campaigns["total_budget"] = pd.to_numeric(campaigns["total_budget"], errors="coerce").fillna(0.0)
    campaigns.to_parquet(f"{SILVER_MDB}/campaigns.parquet", index=False)
    log.info("Campaigns: %d rows saved.", len(campaigns))

    # ---- ad_spend (MongoDB) ----
    log.info("Cleaning ad_spend…")
    ad_spend = pd.read_json(f"{BRONZE_MDB}/ad_spend.json", orient="records")
    for nc in ["spend", "impressions", "clicks", "conversions", "revenue"]:
        if nc in ad_spend.columns:
            ad_spend[nc] = pd.to_numeric(ad_spend[nc], errors="coerce").fillna(0.0)
    if "date" in ad_spend.columns:
        ad_spend["date"] = pd.to_datetime(ad_spend["date"], errors="coerce")
        ad_spend = ad_spend.dropna(subset=["date"])
    if "spend" in ad_spend.columns:
        ad_spend = ad_spend[ad_spend["spend"] > 0]
    if "clicks" in ad_spend.columns and "impressions" in ad_spend.columns:
        ad_spend["ctr_calculated"] = (
            ad_spend["clicks"] / ad_spend["impressions"].replace(0, float("nan"))
        )
    ad_spend.to_parquet(f"{SILVER_MDB}/ad_spend.parquet", index=False)
    log.info("Ad spend: %d rows saved.", len(ad_spend))

    # ---- clicks (MongoDB) ----
    log.info("Cleaning clicks…")
    clicks = pd.read_json(f"{BRONZE_MDB}/clicks.json", orient="records")
    for nc in ["clicks", "impressions", "conversions"]:
        if nc in clicks.columns:
            clicks[nc] = pd.to_numeric(clicks[nc], errors="coerce").fillna(0)
    clicks.to_parquet(f"{SILVER_MDB}/clicks.parquet", index=False)
    log.info("Clicks: %d rows saved.", len(clicks))


# ===========================================================================
# Task 5 — load_snowflake
# ===========================================================================
def load_snowflake() -> None:
    """Upload all silver-layer parquets to Snowflake RAW schema."""
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas

    log = logging.getLogger("load_snowflake")

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )
    cur = conn.cursor()
    db     = os.getenv("SNOWFLAKE_DATABASE", "ECOMMERCE_DB")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "RAW")

    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    cur.execute(f"USE DATABASE {db}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    cur.execute(f"USE SCHEMA {schema}")

    datasets = [
        (f"{SILVER_MDB}/ad_spend.parquet",   "AD_SPEND"),
        (f"{SILVER_MDB}/campaigns.parquet",   "CAMPAIGNS"),
        (f"{SILVER_MDB}/clicks.parquet",      "CLICKS"),
        (f"{SILVER_PG}/customers.parquet",    "CUSTOMERS"),
        (f"{SILVER_PG}/order_items.parquet",  "ORDER_ITEMS"),
        (f"{SILVER_PG}/orders.parquet",       "ORDERS"),
        (f"{SILVER_PG}/products.parquet",     "PRODUCTS"),
        (f"{SILVER_PG}/reviews.parquet",      "REVIEWS"),
    ]

    try:
        for path, table in datasets:
            if not os.path.exists(path):
                log.warning("Skipping %s — file not found: %s", table, path)
                continue
            log.info("Loading %s → %s.%s", path, schema, table)
            df = pd.read_parquet(path)
            df.columns = [c.upper() for c in df.columns]
            # Make datetimes tz-naive for Snowflake
            for col in df.select_dtypes(include=["datetimetz"]).columns:
                df[col] = df[col].dt.tz_convert(None)
            success, chunks, rows, _ = write_pandas(
                conn=conn, df=df, table_name=table,
                auto_create_table=True, overwrite=True,
            )
            if success:
                log.info("✅ %s — %d rows in %d chunks", table, rows, chunks)
            else:
                log.error("❌ Failed to load %s", table)
    finally:
        conn.close()
        log.info("Snowflake connection closed.")


# ===========================================================================
# DAG definition
# ===========================================================================
with DAG(
    dag_id="ecommerce_etl_pipeline",
    description="E-Commerce ETL: Postgres + MongoDB → Transform → Snowflake → dbt MARTS",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "etl", "snowflake", "dbt"],
) as dag:

    t_extract_postgres = PythonOperator(
        task_id="extract_postgres",
        python_callable=extract_postgres,
    )

    t_extract_mongodb = PythonOperator(
        task_id="extract_mongodb",
        python_callable=extract_mongodb,
    )

    t_transform_orders = PythonOperator(
        task_id="transform_orders",
        python_callable=transform_orders,
    )

    t_transform_products = PythonOperator(
        task_id="transform_products",
        python_callable=transform_products,
    )

    t_load_snowflake = PythonOperator(
        task_id="load_snowflake",
        python_callable=load_snowflake,
    )

    t_dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"""
        set -e
        cd {DBT_PROJECT}
        dbt build --profiles-dir . --project-dir . --target dev
        """,
        env={
            "SNOWFLAKE_ACCOUNT":   "{{{{ var.value.get('SNOWFLAKE_ACCOUNT', '') }}}}",
            "SNOWFLAKE_USER":      "{{{{ var.value.get('SNOWFLAKE_USER', '') }}}}",
            "SNOWFLAKE_PASSWORD":  "{{{{ var.value.get('SNOWFLAKE_PASSWORD', '') }}}}",
            "SNOWFLAKE_WAREHOUSE": "{{{{ var.value.get('SNOWFLAKE_WAREHOUSE', '') }}}}",
            "SNOWFLAKE_DATABASE":  "{{{{ var.value.get('SNOWFLAKE_DATABASE', '') }}}}",
            "SNOWFLAKE_SCHEMA":    "{{{{ var.value.get('SNOWFLAKE_SCHEMA', '') }}}}",
            "SNOWFLAKE_ROLE":      "{{{{ var.value.get('SNOWFLAKE_ROLE', '') }}}}",
        },
    )

    # ── Pipeline graph ─────────────────────────────────────────────────────
    #
    #   extract_postgres ──► transform_orders   ──┐
    #                    └──► transform_products──┤
    #   extract_mongodb  ──► transform_products ──┘
    #                                             │
    #                                       load_snowflake
    #                                             │
    #                                          dbt_build
    #
    t_extract_postgres >> t_transform_orders
    [t_extract_postgres, t_extract_mongodb] >> t_transform_products
    [t_transform_orders, t_transform_products] >> t_load_snowflake
    t_load_snowflake >> t_dbt_build
