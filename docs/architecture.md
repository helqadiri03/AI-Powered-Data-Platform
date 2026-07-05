# System Architecture

The AI-Powered E-Commerce Data Platform is composed of multiple interconnected layers, bridging raw operational data to an intelligent, natural-language query interface.

## High-Level Data Flow

```mermaid
flowchart TD
    subgraph Operational Data
        PG[(PostgreSQL\nOrders/Products)]
        MDB[(MongoDB\nMarketing)]
    end

    subgraph Data Lake (Local Filesystem)
        BZ[Bronze Layer\nRaw Extracts]
        SL[Silver Layer\nCleaned/Deduped]
    end
    
    subgraph Cloud Data Warehouse (Snowflake)
        RAW[(RAW Schema)]
        STG[(STAGING Views)]
        INT[(INTERMEDIATE)]
        MRT[(MARTS Schema\nStar Schema)]
    end
    
    subgraph Orchestration
        AF((Apache Airflow))
    end
    
    subgraph Serving & UI
        API[FastAPI\nText-to-SQL Backend]
        LLM[Groq Llama 3.3\nLLM Agent]
        UI[React UI\nVite SPA]
    end

    %% Data flow connections
    PG -->|Airflow extract| BZ
    MDB -->|Airflow extract| BZ
    BZ -->|Airflow Pandas transforms| SL
    SL -->|Airflow snowflake-connector| RAW
    
    RAW -->|dbt build| STG
    STG -->|dbt build| INT
    INT -->|dbt build| MRT
    
    MRT <-->|Queries| API
    API <-->|System Prompt + Schema| LLM
    API <-->|JSON + SQL| UI
    
    %% Orchestration links
    AF -.->|Schedules & Triggers| PG
    AF -.->|Schedules & Triggers| MDB
    AF -.->|Triggers| STG
```

## Component Breakdown

1. **Sources**:
   - **PostgreSQL**: Simulates an operational e-commerce database (Customers, Orders, Items, Products, Reviews).
   - **MongoDB**: Simulates a NoSQL marketing datastore (Campaigns, Ad Spend, Clicks).

2. **Data Lake (Bronze/Silver)**:
   - Data is extracted as Parquet and JSON files to local storage (`/data/bronze/`).
   - Airflow tasks use Pandas to clean, format timestamps, and deduplicate data, writing to `/data/silver/`.

3. **Cloud Data Warehouse (Snowflake)**:
   - Silver data is bulk-loaded into the `RAW` schema.
   - **dbt (Data Build Tool)** transforms the raw tables into a Kimball-style Star Schema located in the `MARTS` schema.

4. **Intelligent Serving Layer**:
   - **FastAPI**: Hosts the agentic logic.
   - **Text-to-SQL Agent**: Uses Groq (Llama 3.3 70B) to translate natural language into SQL.
   - **SQL Validator**: Uses `sqlglot` to parse the generated SQL, enforce security constraints (read-only, target `MARTS` schema only), and inject execution limits.

5. **Frontend**:
   - A modern React application with a glassmorphism design that interacts with the FastAPI backend, displaying generated SQL and formatted result tables.
