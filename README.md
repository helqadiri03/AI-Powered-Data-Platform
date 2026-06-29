# AI-Powered E-Commerce Platform

End-to-end data platform with Airflow ETL, Snowflake warehouse, FastAPI backend, Text-to-SQL agent, RAG assistant, and Grafana monitoring.

## Architecture

```
Sources (Marketing API + Postgres + CSV)
    → ETL (Airflow DAGs)
    → Snowflake (staging → warehouse → analytics)
    → FastAPI (query, RAG, validation, monitoring)
    → React dashboard (optional)
```

## Quick start

```bash
# 1. Copy and fill secrets
cp .env.example .env   # or edit .env directly

# 2. Start the stack
docker compose up -d

# 3. Open services
# Airflow UI:    http://localhost:8080  (airflow / airflow)
# FastAPI docs:  http://localhost:8000/docs
# Marketing API: http://localhost:8001/docs
# Prometheus:    http://localhost:9090
# Grafana:       http://localhost:3000  (admin / admin)
```

## Project layout

| Path | Purpose |
|------|---------|
| `dags/` | Airflow DAG definitions |
| `etl/` | Extract, transform, load Python package |
| `sources/` | Fake marketing API + Postgres seed SQL |
| `data/sales/` | CSV sales files (Source B) |
| `snowflake/` | Staging, warehouse, and KPI SQL |
| `backend/` | FastAPI application |
| `agent/` | Text-to-SQL agent |
| `validation/` | SQL safety and semantic validation |
| `rag/` | RAG ingestion and retrieval |
| `monitoring/` | Prometheus + Grafana configs |
| `frontend/` | React dashboard (optional) |

## Development

```bash
python -m venv env && source env/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

## Phases

1. **Infrastructure** — Docker Compose (Postgres, Airflow, FastAPI, monitoring)
2. **Data sources** — Marketing API, CSV sales, Postgres seeds
3. **ETL** — Airflow DAG orchestrating extract → transform → load
4. **Snowflake** — Staging tables, star schema, KPI queries
5. **Backend API** — Query, RAG, validation, monitoring endpoints
6. **Agent** — Natural language → SQL → Snowflake
7. **RAG** — Documentation assistant over vector store
8. **Frontend** — React dashboard (optional)
