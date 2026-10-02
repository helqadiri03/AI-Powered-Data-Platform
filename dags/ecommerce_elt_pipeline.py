"""
ecommerce_elt_pipeline DAG
===========================
Full end-to-end ELT pipeline (Extract → Load → Transform):

  extract_postgres  ─┐
                     ├─► load_snowflake ──► dbt_build
  extract_mongodb  ──┘

Task breakdown:
  1. extract_postgres  – Reads all tables from PostgreSQL and bulk-loads them
                         directly into the Snowflake RAW schema.
  2. extract_mongodb   – Reads campaigns/ad_spend/clicks from MongoDB and
                         bulk-loads them directly into the Snowflake RAW schema.
  3. load_snowflake    – Gate task: waits for both extracts to complete before
                         signalling dbt.  (kept as a no-op sensor step for
                         clarity; actual loading happens inside the extractors.)
  4. dbt_build         – Runs `dbt build` to materialise
                         RAW → STAGING → INTERMEDIATE → MARTS

ELT philosophy:
  Data is extracted and loaded into the cloud warehouse **as-is** (raw).
  All business logic, type casting, deduplication, and modelling are performed
  inside the warehouse by dbt — keeping transformation logic version-controlled
  and warehouse-native.

Schedule: daily at 02:00 UTC
"""

from __future__ import annotations

import json
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
# Path constants (relative to project root mounted into Airflow at /opt/airflow)
# ---------------------------------------------------------------------------
PROJECT_ROOT = "/opt/airflow"
DBT_PROJECT  = f"{PROJECT_ROOT}/ecommerce_dbt"


# ---------------------------------------------------------------------------
# Shared Snowflake helper
# ---------------------------------------------------------------------------
def _get_snowflake_conn():
    """Return an open Snowflake connector connection."""
    import snowflake.connector

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )


def _ensure_schema(cur, db: str, schema: str) -> None:
    """Create database and schema if they do not already exist."""
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    cur.execute(f"USE DATABASE {db}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    cur.execute(f"USE SCHEMA {schema}")


def _load_df_to_snowflake(conn, df: pd.DataFrame, table: str, log) -> None:
    """Upper-case column names and write a DataFrame into Snowflake."""
    from snowflake.connector.pandas_tools import write_pandas

    df.columns = [c.upper() for c in df.columns]

    # Snowflake's write_pandas does not support timezone-aware timestamps
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_convert(None)

    success, chunks, rows, _ = write_pandas(
        conn=conn,
        df=df,
        table_name=table,
        auto_create_table=True,
        overwrite=True,
    )
    if success:
        log.info("✅ %s — %d rows in %d chunks", table, rows, chunks)
    else:
        log.error("❌ Failed to load %s", table)


# ===========================================================================
# Task 1 — extract_postgres
# ===========================================================================
def extract_postgres() -> None:
    """
    Extract all relational tables from PostgreSQL and load them directly into
    the Snowflake RAW schema (ELT: no local transformation before loading).
    """
    from sqlalchemy import create_engine

    log = logging.getLogger("extract_postgres")

    # ── Connect to PostgreSQL ───────────────────────────────────────────────
    pg_host = os.getenv("POSTGRES_HOST", "db")
    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
    pg_db   = os.getenv("POSTGRES_DB", "ai_powered_eco_db")

    engine = create_engine(
        f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}/{pg_db}"
    )

    tables = {
        "CUSTOMERS":   "SELECT * FROM customers",
        "ORDERS":      "SELECT * FROM orders",
        "ORDER_ITEMS": "SELECT * FROM order_items",
        "PRODUCTS":    "SELECT * FROM products",
        "REVIEWS":     "SELECT * FROM reviews",
    }

    # ── Connect to Snowflake ────────────────────────────────────────────────
    conn = _get_snowflake_conn()
    cur  = conn.cursor()
    db     = os.getenv("SNOWFLAKE_DATABASE", "ECOMMERCE_DB")
    schema = "RAW"

    try:
        _ensure_schema(cur, db, schema)

        for table, query in tables.items():
            log.info("Extracting table: %s", table)
            df = pd.read_sql(query, engine)
            log.info("Extracted %d rows from PostgreSQL → %s", len(df), table)
            _load_df_to_snowflake(conn, df, table, log)

    finally:
        conn.close()
        log.info("PostgreSQL ELT extraction complete.")


# ===========================================================================
# Task 2 — extract_mongodb
# ===========================================================================
def extract_mongodb() -> None:
    """
    Extract marketing collections from MongoDB and load them directly into
    the Snowflake RAW schema (ELT: no local transformation before loading).
    """
    from pymongo import MongoClient

    log = logging.getLogger("extract_mongodb")

    # ── Connect to MongoDB ──────────────────────────────────────────────────
    mongo_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/")
    client = MongoClient(mongo_url)
    db_mongo = client["marketing_db"]

    collections = {
        "CAMPAIGNS": "campaign",
        "AD_SPEND":  "ad_spend",
        "CLICKS":    "clicks",
    }

    # ── Connect to Snowflake ────────────────────────────────────────────────
    conn = _get_snowflake_conn()
    cur  = conn.cursor()
    db     = os.getenv("SNOWFLAKE_DATABASE", "ECOMMERCE_DB")
    schema = "RAW"

    try:
        _ensure_schema(cur, db, schema)

        for table, col_name in collections.items():
            log.info("Extracting collection: %s", col_name)
            docs = list(db_mongo[col_name].find())
            df = pd.DataFrame(docs)
            if "_id" in df.columns:
                # MongoDB ObjectIDs are not serialisable; drop before loading
                df.drop(columns=["_id"], inplace=True)
            log.info("Extracted %d documents from MongoDB → %s", len(df), table)
            _load_df_to_snowflake(conn, df, table, log)

    finally:
        client.close()
        conn.close()
        log.info("MongoDB ELT extraction complete.")


# ===========================================================================
# DAG definition
# ===========================================================================
with DAG(
    dag_id="ecommerce_elt_pipeline",
    description=(
        "E-Commerce ELT: Postgres + MongoDB → Snowflake RAW → dbt MARTS. "
        "All transformations are performed inside Snowflake by dbt."
    ),
    default_args=DEFAULT_ARGS,
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "elt", "snowflake", "dbt"],
) as dag:

    t_extract_postgres = PythonOperator(
        task_id="extract_postgres",
        python_callable=extract_postgres,
        doc_md=(
            "Reads all e-commerce tables from PostgreSQL and bulk-loads them "
            "into the Snowflake RAW schema using `write_pandas`."
        ),
    )

    t_extract_mongodb = PythonOperator(
        task_id="extract_mongodb",
        python_callable=extract_mongodb,
        doc_md=(
            "Reads marketing collections from MongoDB and bulk-loads them "
            "into the Snowflake RAW schema using `write_pandas`."
        ),
    )

    t_dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"""
        set -e
        cd {DBT_PROJECT}
        dbt build --profiles-dir . --project-dir . --target dev
        """,
        env={
            "SNOWFLAKE_ACCOUNT":   "{{ var.value.get('SNOWFLAKE_ACCOUNT', '') }}",
            "SNOWFLAKE_USER":      "{{ var.value.get('SNOWFLAKE_USER', '') }}",
            "SNOWFLAKE_PASSWORD":  "{{ var.value.get('SNOWFLAKE_PASSWORD', '') }}",
            "SNOWFLAKE_WAREHOUSE": "{{ var.value.get('SNOWFLAKE_WAREHOUSE', '') }}",
            "SNOWFLAKE_DATABASE":  "{{ var.value.get('SNOWFLAKE_DATABASE', '') }}",
            "SNOWFLAKE_SCHEMA":    "{{ var.value.get('SNOWFLAKE_SCHEMA', '') }}",
            "SNOWFLAKE_ROLE":      "{{ var.value.get('SNOWFLAKE_ROLE', '') }}",
        },
        doc_md=(
            "Runs `dbt build` against the Snowflake warehouse. "
            "Transforms RAW tables through STAGING → INTERMEDIATE → MARTS."
        ),
    )

    # ── Pipeline graph ──────────────────────────────────────────────────────
    #
    #   extract_postgres ──┐
    #                      ├──► dbt_build
    #   extract_mongodb  ──┘
    #
    [t_extract_postgres, t_extract_mongodb] >> t_dbt_build
