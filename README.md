# AI-Powered E-Commerce Data Platform

This repository contains a full-stack, AI-powered e-commerce data platform. It extracts data from operational databases (PostgreSQL and MongoDB), transforms and loads it into Snowflake via Apache Airflow and dbt, and provides a modern React interface to query the data using natural language, powered by Groq and Llama 3.3.

## 🚀 Features

* **Automated ETL Pipeline**: Nightly extraction from Postgres (sales data) and MongoDB (marketing data) to a local data lake (Bronze/Silver), loading into Snowflake (RAW).
* **dbt Transformations**: Kimball dimensional modeling inside Snowflake to produce high-performance `MARTS` tables (e.g., `FACT_SALES`, `DIM_CUSTOMER`).
* **Text-to-SQL Agent**: FastAPI backend uses Groq (`llama-3.3-70b-versatile`) to translate natural language questions into Snowflake SQL.
* **Strict SQL Validation**: Ensures the AI only generates safe `SELECT` queries targeting the `MARTS` schema using `sqlglot`.
* **Glassmorphism React UI**: A premium, modern frontend built with Vite and React for natural language data exploration.

## 🏗 Architecture Overview

1. **Source Databases**: Postgres (Orders, Products) & MongoDB (Marketing Campaigns).
2. **Orchestration**: Apache Airflow schedules the `ecommerce_etl_pipeline` DAG.
3. **Data Warehouse**: Snowflake stores the `RAW` data and the transformed `MARTS`.
4. **Transformations**: dbt (`ecommerce_dbt`) handles the modeling from staging to marts.
5. **Backend**: FastAPI exposes the `/api/query` endpoint for the Text-to-SQL pipeline.
6. **Frontend**: Vite + React single-page application.

*See `docs/architecture.md` for a detailed diagram and flow.*

## ⚙️ Quickstart

### Prerequisites
- Docker and Docker Compose installed.
- A Snowflake account with a warehouse, database, and role configured.
- A Groq API key for the Text-to-SQL agent.

### Setup
1. **Environment Variables**: Clone the repository and configure your `.env` file in the project root:
   ```env
   # Snowflake config
   SNOWFLAKE_ACCOUNT=<your_account>
   SNOWFLAKE_USER=<your_user>
   SNOWFLAKE_PASSWORD=<your_password>
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=ECOMMERCE_DB
   SNOWFLAKE_SCHEMA=RAW
   SNOWFLAKE_ROLE=ACCOUNTADMIN

   # Groq Text-to-SQL
   GROQ_API_KEY=gsk_your_key_here
   ```

2. **Start the Stack**:
   ```bash
   docker-compose up -d --build
   ```
   This will spin up Postgres, MongoDB, Airflow, the FastAPI backend, and the React frontend.

3. **Run the ETL**:
   - Access Airflow at `http://localhost:8080` (admin/airflow).
   - Trigger the `ecommerce_etl_pipeline` DAG.
   - Wait for it to complete (Extract -> Transform -> Load Snowflake -> dbt build).

4. **Explore the Data**:
   - Access the React UI at `http://localhost:5173`.
   - Ask a question like "What were the top 10 products by revenue?".

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

* [Architecture & System Design](docs/architecture.md)
* [Airflow & Orchestration](docs/airflow.md)
* [ETL Pipeline Details](docs/etl.md)
* [dbt Modeling](docs/dbt.md)
* [Snowflake Configuration](docs/snowflake.md)
* [Text-to-SQL Agent](docs/text_to_sql.md)
* [FastAPI Backend](docs/api.md)
* [Monitoring & Observability](docs/monitoring.md)
* [Data Dictionary: FACT_SALES](docs/fact_sales.md)
* [Data Dictionary: DIM_CUSTOMER](docs/dim_customer.md)
