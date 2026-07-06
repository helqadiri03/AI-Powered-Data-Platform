# AI-Powered E-Commerce Analytics Platform

> **An end-to-end Modern Data Platform combining Data Engineering, Analytics Engineering, Artificial Intelligence, and MLOps to enable natural language analytics over an enterprise-grade E-Commerce Data Warehouse.**

---

# Overview

This project demonstrates how modern organizations can build an AI-powered analytics platform capable of transforming raw transactional data into business insights using natural language.

Instead of writing SQL queries manually, business users can simply ask questions such as:

> **"Which products generated the highest revenue last month?"**

or

> **"Show the monthly sales trend by country."**

The platform automatically:

- Ingests raw transactional data
- Orchestrates ELT pipelines
- Transforms data into a dimensional warehouse
- Validates AI-generated SQL
- Executes queries on Snowflake
- Explains results using Large Language Models
- Answers documentation questions using Retrieval-Augmented Generation (RAG)

The entire infrastructure is containerized and follows modern Data Engineering best practices used in enterprise environments.

---

# Features

## Modern ELT Pipeline

- PostgreSQL source database
- Automated ingestion into Snowflake
- Apache Airflow orchestration
- dbt transformations
- Incremental models
- Data quality tests
- Medallion Architecture (Bronze → Silver → Gold)

---

## Enterprise Data Warehouse

The warehouse follows the **Kimball Dimensional Modeling** methodology.

### Fact Tables

- Fact Sales
- Fact Orders
- Fact Revenue

### Dimension Tables

- Customer
- Product
- Category
- Supplier
- Geography
- Date

This structure enables fast analytical queries and supports BI tools efficiently.

---

## AI Text-to-SQL Assistant

Business users can ask questions in natural language.

Example:

> Which category generated the highest revenue in 2024?

The system automatically:

1. Understands the request
2. Generates SQL using Llama 3
3. Validates the generated SQL
4. Prevents unsafe queries
5. Executes the query on Snowflake
6. Returns structured results
7. Generates a natural language explanation

---

## AI Documentation Assistant (RAG)

The platform includes an intelligent documentation chatbot powered by:

- LangChain
- Pinecone
- Groq Llama 3

It can answer questions about:

- Data models
- Pipelines
- Business definitions
- Architecture
- Documentation
- Warehouse schema

Example:

> What is the purpose of the Gold layer?

---

## Data Quality

Using **dbt Tests**:

- Unique constraints
- Not Null validation
- Accepted values
- Referential integrity
- Relationship testing

This guarantees trusted analytical datasets.

---

## Monitoring & Observability

Real-time monitoring using:

- Prometheus
- Grafana

Tracked metrics include:

- API latency
- SQL generation time
- LLM response time
- Pipeline execution
- Airflow task status
- Request throughput
- Error rate
- Container health

---

## Secure SQL Execution

The platform never executes raw LLM output directly.

Generated SQL is:

- Parsed
- Validated
- Sanitized
- Restricted to SELECT statements
- Checked against the warehouse schema

using **SQLGlot** before execution.

---

# Architecture

```text
                        +----------------------+
                        |    React Frontend    |
                        +----------+-----------+
                                   |
                                   |
                         FastAPI Backend
                                   |
      ---------------------------------------------------
      |                     |                          |
      |                     |                          |
 Text-to-SQL          Documentation AI         Monitoring API
      |                     |                          |
      |                     |                          |
   Groq LLM             LangChain                  Prometheus
      |                     |
      |                 Pinecone
      |
  SQL Validation
     (SQLGlot)
      |
      |
  Snowflake Data Warehouse
      |
      |
  -------------------------------
  |             |               |
 Bronze       Silver          Gold
      ^
      |
Apache Airflow
      |
PostgreSQL
```

---

# Technology Stack

## Data Engineering

| Technology | Purpose |
|------------|----------|
| PostgreSQL | Source transactional database |
| Snowflake | Cloud Data Warehouse |
| Apache Airflow | Workflow orchestration |
| dbt | Data transformation |
| SQLAlchemy | Database connectivity |

---

## Artificial Intelligence

| Technology | Purpose |
|------------|----------|
| Groq | Ultra-fast LLM inference |
| Llama 3.3 70B | Text-to-SQL & RAG |
| LangChain | AI orchestration |
| Pinecone | Vector database |
| SQLGlot | SQL validation & parsing |

---

## Backend

| Technology | Purpose |
|------------|----------|
| FastAPI | REST API |
| Python | Backend language |
| Pydantic | Data validation |
| Uvicorn | ASGI server |

---

## Frontend

| Technology | Purpose |
|------------|----------|
| React | User Interface |
| TypeScript | Type safety |
| Vite | Frontend tooling |
| Tailwind CSS | Styling |
| Axios | API communication |

---

## Monitoring

| Technology | Purpose |
|------------|----------|
| Prometheus | Metrics collection |
| Grafana | Dashboard visualization |
| StatsD | Airflow metrics |

---

## DevOps

| Technology | Purpose |
|------------|----------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |

---

# Project Structure

```text
AI-Ecommerce-Platform/

├── airflow/
│   ├── dags/
│   ├── plugins/
│   └── logs/
│
├── backend/
│   ├── api/
│   ├── rag/
│   ├── text_to_sql/
│   ├── services/
│   ├── monitoring/
│   └── core/
│
├── frontend/
│
├── dbt/
│   ├── models/
│   │   ├── bronze/
│   │   ├── silver/
│   │   └── gold/
│   ├── tests/
│   ├── snapshots/
│   └── macros/
│
├── postgres/
│
├── grafana/
│
├── prometheus/
│
├── docs/
│
├── docker-compose.yml
│
├── .env.example
│
└── README.md
```

---

# Data Pipeline

```text
PostgreSQL
      │
      ▼
Apache Airflow
      │
      ▼
Snowflake Bronze
      │
      ▼
dbt Transformations
      │
      ▼
Snowflake Silver
      │
      ▼
Snowflake Gold
      │
      ▼
Analytics & AI Services
```

---

# Text-to-SQL Workflow

```text
User Question
      │
      ▼
Groq Llama 3
      │
      ▼
Generated SQL
      │
      ▼
SQLGlot Validation
      │
      ▼
Snowflake Execution
      │
      ▼
Results
      │
      ▼
Natural Language Explanation
```

---

# RAG Workflow

```text
Documentation
      │
      ▼
Document Chunking
      │
      ▼
Embeddings
      │
      ▼
Pinecone Vector Store
      │
      ▼
Similarity Search
      │
      ▼
Groq LLM
      │
      ▼
Final Answer
```

---

# Infrastructure

Everything runs inside Docker containers.

Included services:

- React Frontend
- FastAPI Backend
- PostgreSQL
- Apache Airflow
- Snowflake Connector
- dbt
- Prometheus
- Grafana
- Pinecone Integration
- Groq Integration

Start the complete platform with:

```bash
docker compose up --build
```

---

# Getting Started

## Prerequisites

- Docker
- Docker Compose
- Snowflake Account
- Groq API Key
- Pinecone API Key

---

## Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Ecommerce-Platform.git

cd AI-Ecommerce-Platform
```

---

## Configure Environment Variables

Create a `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ecommerce

SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_ROLE=

GROQ_API_KEY=

PINECONE_API_KEY=
PINECONE_INDEX=ecommerce-docs

FERNET_KEY=

GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

---

## Launch the Platform

```bash
docker compose up --build
```

---

## Available Services

| Service | URL |
|----------|-----|
| React Frontend | http://localhost:5173 |
| FastAPI Docs | http://localhost:8000/docs |
| Airflow | http://localhost:8080 |
| Grafana | http://localhost:3000 |

---

## Load the Data

1. Open Airflow.
2. Enable the ELT DAG.
3. Trigger the pipeline.
4. Wait for completion.
5. Start querying your warehouse using natural language.

---

# Future Improvements

- Role-Based Access Control (RBAC)
- Semantic Layer
- Automatic Dashboard Generation
- Multi-Agent AI
- Fine-tuned SQL Generation
- Kafka Streaming Pipelines
- Kubernetes Deployment
- GitHub Actions CI/CD
- Great Expectations Integration
- ML-Based Anomaly Detection
- Cost Monitoring for Snowflake

---

# Skills Demonstrated

- Data Engineering
- Analytics Engineering
- Cloud Data Warehousing
- Snowflake
- Apache Airflow
- dbt
- PostgreSQL
- FastAPI
- React
- TypeScript
- Docker
- Prometheus
- Grafana
- Artificial Intelligence
- Large Language Models
- Text-to-SQL
- Retrieval-Augmented Generation (RAG)
- Vector Databases
- SQL Validation
- Enterprise Data Architecture
- Kimball Dimensional Modeling
- Medallion Architecture
- Observability
- Modern ELT Pipelines

---

# License

This project is intended for educational, research, and portfolio purposes.
