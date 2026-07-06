"""
POST /api/query

Orchestrates the full pipeline:
  Natural Language → Text-to-SQL Agent → SQL Validation → Snowflake → Response
"""

from __future__ import annotations

import time
import logging

from fastapi import APIRouter

from agents.text_to_sql import generate_sql
from agents.sql_validator import validate_and_sanitize
from db.snowflake_client import run_query
from schemas.query import QueryRequest, QueryResponse
from metrics import (
    SQL_GENERATION_DURATION,
    SQL_EXECUTION_DURATION,
    SQL_REQUEST_TOTAL,
)

router = APIRouter(prefix="/api", tags=["Query"])

logger = logging.getLogger(__name__)


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Natural language query against Snowflake MARTS",
    description=(
        "Accepts a plain-English question, translates it to SQL using an LLM, "
        "validates the SQL for safety, executes it against Snowflake MARTS, "
        "and returns structured results."
    ),
)
async def natural_language_query(payload: QueryRequest) -> QueryResponse:
    question = payload.question
    logger.info("Received question: %s", question)

    try:
        # Step 1 — Text-to-SQL (LLM, timed)
        t0 = time.perf_counter()
        raw_sql, model_used = generate_sql(question)
        SQL_GENERATION_DURATION.observe(time.perf_counter() - t0)

        # Step 2 — SQL Validation Layer
        safe_sql = validate_and_sanitize(raw_sql)

        # Step 3 — Execute against Snowflake MARTS (timed separately)
        t1 = time.perf_counter()
        result = run_query(safe_sql)
        SQL_EXECUTION_DURATION.observe(time.perf_counter() - t1)

        SQL_REQUEST_TOTAL.labels(status="success").inc()

        return QueryResponse(
            question=question,
            sql=safe_sql,
            model_used=model_used,
            columns=result["columns"],
            rows=result["rows"],
            row_count=result["row_count"],
        )
    except Exception as e:
        SQL_REQUEST_TOTAL.labels(status="error").inc()
        raise
