# FastAPI Backend

The backend of the platform is built using FastAPI, providing a high-performance asynchronous API for the React frontend.

## API Endpoints

### `POST /api/query`
The primary endpoint that orchestrates the Text-to-SQL pipeline.

**Request Body:**
```json
{
  "question": "What were the top 10 products by revenue?"
}
```

**Response Body:**
```json
{
  "question": "What were the top 10 products by revenue?",
  "sql": "SELECT product_category_name, SUM(price) ...",
  "model_used": "llama-3.3-70b-versatile",
  "columns": ["PRODUCT_CATEGORY_NAME", "TOTAL_REVENUE"],
  "rows": [
    ["electronics", 54320.0],
    ["health_beauty", 42100.5]
  ],
  "row_count": 2
}
```

### `GET /health`
A simple healthcheck endpoint utilized by Docker Compose to verify the service is running before starting dependent services.

## Configuration Management

Configuration is handled robustly using `pydantic-settings`. 

The `Settings` class (`api/config.py`) parses the `.env` file and strictly validates the presence of required variables (Snowflake credentials, Groq API key). It also establishes defaults for the LLM models and row limits.

## CORS & Routing

During local development, Cross-Origin Resource Sharing (CORS) is handled by configuring the Vite frontend to proxy `/api` requests to the FastAPI service running on port `8000`. This prevents browser CORS preflight blocks.
