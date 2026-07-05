# Monitoring & Observability

The platform includes a monitoring stack utilizing Prometheus and Grafana.

*(Note: Currently configured in `docker-compose.yml` but marked for future phases of dashboard development)*

## Prometheus
- **Purpose**: Time-series database that scrapes metrics from the FastAPI service and Airflow instances.
- **Port**: `9090`.

## Grafana
- **Purpose**: Visualization layer on top of Prometheus.
- **Port**: `3000`.
- **Default Credentials**: admin / admin.

Future expansions will include dedicated dashboards tracking:
1. ETL pipeline duration and success rates.
2. Text-to-SQL LLM token usage and latency.
3. FastAPI endpoint request rates and 4xx/5xx error codes.
