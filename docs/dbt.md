# dbt Modeling

The dbt (Data Build Tool) project transforms the raw data loaded into Snowflake into a highly performant, analytics-ready Star Schema.

The dbt project is located in `ecommerce_dbt/`.

## Architecture Layers

The dbt project strictly follows dbt Labs' recommended multi-layer architecture:

### 1. Staging (`models/staging/`)
- **Purpose**: A 1:1 mapping to the `RAW` tables in Snowflake, adding standard naming conventions, type casting, and minor logic.
- **Materialization**: `view`.
- **Naming**: Prefixed with `stg_`.
- **Examples**: `stg_postgres_orders`, `stg_mongodb_campaigns`.

### 2. Intermediate (`models/intermediate/`)
- **Purpose**: Joins staging models together, aggregates data to different grains, and prepares the foundations for the Marts layer.
- **Materialization**: `view` or `ephemeral`.
- **Naming**: Prefixed with `int_`.
- **Examples**: `int_customer_order_history`, `int_campaign_performance`.

### 3. Marts (`models/marts/`)
- **Purpose**: The final, business-facing Star Schema optimized for BI tools and our Text-to-SQL AI Agent.
- **Materialization**: `table` (for high query performance).
- **Naming**: Prefixed with `fact_` (transactional data) or `dim_` (descriptive entities).
- **Examples**: `fact_sales`, `fact_marketing`, `dim_customer`, `dim_product`, `dim_campaign`.

## Configuration overrides

### Custom Schema Generation
By default, dbt appends the target schema name to the environment's default schema (e.g., `RAW_MARTS`). We override this behavior using a macro (`macros/generate_schema_name.sql`) to ensure that models materialize directly into the target schema (e.g., exactly `MARTS`), providing a cleaner namespace for the AI Agent.

### Profiles (`profiles.yml`)
The `profiles.yml` is configured to read directly from environment variables passed by the Airflow `BashOperator`:
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

## Running dbt
dbt is automatically triggered by Airflow at the end of the ETL pipeline via:
```bash
dbt build --profiles-dir . --project-dir . --target dev
```
The `dbt build` command elegantly runs models, seeds, and tests sequentially based on the DAG dependencies defined via `ref()` functions within the SQL files.
