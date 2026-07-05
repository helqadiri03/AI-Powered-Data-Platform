# Data Dictionary: DIM_CUSTOMER

`DIM_CUSTOMER` is a core dimension table in the `MARTS` schema. It contains descriptive attributes for all customers who have placed orders on the platform.

## Schema Definition

| Column | Type | Description |
|---|---|---|
| `CUSTOMER_ID` | STRING | Unique identifier for the customer (Primary Key) |
| `CUSTOMER_UNIQUE_ID` | STRING | An alternative unique identifier linking multiple orders |
| `CUSTOMER_ZIP_CODE_PREFIX` | STRING | The prefix of the customer's zip code |
| `CUSTOMER_CITY` | STRING | The city where the customer is located |
| `CUSTOMER_STATE` | STRING | The state where the customer is located |

## Lineage

1. **Sources**: `RAW.CUSTOMERS`
2. **Staging**: `STG_POSTGRES_CUSTOMERS`
3. **Marts**: `DIM_CUSTOMER`

*Materialized as a Table via dbt.*
