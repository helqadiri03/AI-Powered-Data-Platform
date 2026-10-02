# ELT Pipeline (Extract, Load, Transform)

The project implements a **pure ELT** architecture. Raw data is extracted from source systems and loaded directly into Snowflake with no intermediate local transformation. All business logic, type casting, deduplication, and modelling are performed inside the warehouse by dbt.

> **Why ELT and not ETL?**
> ELT leverages the elastic compute power of Snowflake to run transformations at scale using SQL, keeping all transformation logic version-controlled in dbt and the warehouse-native. There is no need for a local PySpark or Pandas transformation step before loading.

---

## ELT Data Flow

```text
PostgreSQL / MongoDB
       │
       │  (Extract: raw data as-is)
       ▼
Snowflake RAW Schema
       │
       │  (Transform: dbt runs SQL models)
       ▼
Snowflake STAGING → INTERMEDIATE → MARTS
```

---

## Extract Phase

The Airflow DAG (`dags/ecommerce_elt_pipeline.py`) contains two extraction tasks:

### `extract_postgres` (PythonOperator)
- Connects to PostgreSQL using **SQLAlchemy**.
- Reads tables: `customers`, `orders`, `order_items`, `products`, `reviews`.
- Loads each table **directly** into Snowflake RAW schema using `write_pandas`.
- Column names are upper-cased to comply with Snowflake conventions.
- No local file system writes; data flows in-memory from PostgreSQL → Snowflake.

### `extract_mongodb` (PythonOperator)
- Connects to MongoDB using **PyMongo**.
- Reads collections: `campaign`, `ad_spend`, `clicks`.
- MongoDB `_id` ObjectIDs are stripped to prevent serialisation issues.
- Loads each collection **directly** into Snowflake RAW schema using `write_pandas`.

---

## Load Phase

Both extraction tasks call `write_pandas` from the official `snowflake-connector-python`:

- **Target schema**: `RAW` (auto-created if not exists).
- **Table strategy**: `auto_create_table=True`, `overwrite=True` — tables are recreated on each daily run to guarantee idempotency.
- **Timezone handling**: `datetimetz` columns are converted to tz-naive before loading, as required by Snowflake's `write_pandas`.

---

## Transform Phase (dbt)

After both extract tasks complete, the `dbt_build` BashOperator triggers:

```bash
dbt build --profiles-dir . --project-dir . --target dev
```

dbt then transforms the RAW data through three layers:

| Layer | Schema | Materialization | Purpose |
|-------|--------|-----------------|---------|
| Staging | `STAGING` | View | Type casting, null handling, deduplication |
| Intermediate | `INTERMEDIATE` | View | Joins, aggregations, grain changes |
| Marts | `MARTS` | Table | Star schema (fact + dimension tables) |

All transformation logic that was previously spread across Pandas scripts is now encapsulated in dbt SQL models, making it testable, documentable, and version-controlled.

---

## Snowflake Loading Details

- **Connection**: Official `snowflake-connector-python` package.
- **Bulk loading**: `write_pandas` uses Snowflake's internal staging and `COPY INTO` mechanism for efficient bulk uploads.
- **Column naming**: All columns are upper-cased prior to load, preventing downstream quoting issues in dbt.
- **Schema setup**: The DAG auto-creates the target database and RAW schema if they do not exist.
