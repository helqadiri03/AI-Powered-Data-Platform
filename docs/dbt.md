# dbt Modeling

The dbt (Data Build Tool) project transforms the raw data loaded into Snowflake into a highly performant, analytics-ready Star Schema.

The dbt project is located in `ecommerce_dbt/`.

## ELT Role of dbt

In this **ELT** architecture, dbt is responsible for **all** data transformation. The Airflow pipeline only extracts and loads raw data into Snowflake's `RAW` schema. From that point forward, dbt owns:

- Type casting and coercion (e.g., string → timestamp, string → numeric)
- Null handling and default value substitution
- Deduplication using `QUALIFY ROW_NUMBER()`
- Business-rule filtering (e.g., valid review scores between 1–5)
- Joins and grain changes
- Derived metrics (e.g., click-through rate via Snowflake's `DIV0`)
- Star schema materialisation

This keeps all transformation logic version-controlled, testable, and documented in SQL.

---

## Architecture Layers

The dbt project strictly follows dbt Labs' recommended multi-layer architecture:

### 1. Staging (`models/staging/`)
- **Source**: `RAW` schema — tables populated by Airflow's ELT extraction.
- **Purpose**: A 1:1 mapping to the `RAW` tables, applying type casting, null coalescing, filtering, and deduplication. No business logic.
- **Materialization**: `view`.
- **Naming**: Prefixed with `stg_`.
- **Examples**: `stg_orders`, `stg_customers`, `stg_campaigns`.

### 2. Intermediate (`models/intermediate/`)
- **Purpose**: Joins staging models together, aggregates data to different grains, and prepares the foundations for the Marts layer.
- **Materialization**: `view`.
- **Naming**: Prefixed with `int_`.
- **Examples**: `int_order_items_enriched`, `int_marketing_performance`.

### 3. Marts (`models/marts/`)
- **Purpose**: The final, business-facing Star Schema optimized for BI tools and the Text-to-SQL AI Agent.
- **Materialization**: `table` (for high query performance).
- **Naming**: Prefixed with `fact_` (transactional data) or `dim_` (descriptive entities).
- **Examples**: `fact_sales`, `fact_marketing`, `dim_customer`, `dim_product`, `dim_campaign`.

---

## Schema Layout

| dbt Layer | Snowflake Schema | Materialization |
|-----------|-----------------|-----------------|
| Source     | `RAW`           | Table (loaded by Airflow) |
| Staging    | `STAGING`       | View |
| Intermediate | `INTERMEDIATE` | View |
| Marts      | `MARTS`         | Table |

---

## Configuration Overrides

### Custom Schema Generation
By default, dbt appends the target schema name to the environment's default schema (e.g., `RAW_MARTS`). The `macros/generate_schema_name.sql` macro overrides this behavior so models materialise directly into the target schema (e.g., exactly `MARTS`).

### Profiles (`profiles.yml`)
The `profiles.yml` reads directly from environment variables passed by the Airflow `BashOperator`:
```yaml
ecommerce_dbt:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      # ...
```

---

## Running dbt

dbt is automatically triggered by Airflow at the end of the ELT pipeline via:
```bash
dbt build --profiles-dir . --project-dir . --target dev
```
The `dbt build` command runs models, seeds, and tests sequentially based on the DAG dependencies defined via `ref()` functions within the SQL files.
