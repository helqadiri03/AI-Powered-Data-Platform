# Data Dictionary: FACT_SALES

`FACT_SALES` is the core transactional table in the `MARTS` schema. It contains line-item level details for every product sold in an order.

## Schema Definition

| Column | Type | Description |
|---|---|---|
| `ORDER_ITEM_ID` | STRING | Unique identifier for the order item (Primary Key) |
| `ORDER_ID` | STRING | Foreign key to the order |
| `PRODUCT_ID` | STRING | Foreign key to `DIM_PRODUCT` |
| `CUSTOMER_ID` | STRING | Foreign key to `DIM_CUSTOMER` |
| `SELLER_ID` | STRING | Foreign key to the seller |
| `ORDER_DATE` | TIMESTAMP | The date the order was placed |
| `PRICE` | FLOAT | The price of the product |
| `FREIGHT_VALUE` | FLOAT | The cost of shipping |
| `ORDER_STATUS` | STRING | Status (e.g., delivered, shipped, canceled) |

## Lineage

1. **Sources**: `RAW.ORDERS`, `RAW.ORDER_ITEMS`
2. **Staging**: `STG_POSTGRES_ORDERS`, `STG_POSTGRES_ORDER_ITEMS`
3. **Marts**: `FACT_SALES` is created by joining the staging tables on `ORDER_ID`.

*Materialized as a Table via dbt.*
