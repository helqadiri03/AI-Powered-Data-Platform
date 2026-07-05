"""
POST /api/query

Orchestrates the full pipeline:
  Natural Language → Text-to-SQL Agent → SQL Validation → Snowflake → Response
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from agents.text_to_sql import generate_sql
from agents.sql_validator import validate_and_sanitize
from db.snowflake_client import run_query
from schemas.query import QueryRequest, QueryResponse

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

    # Step 1 — Text-to-SQL
    raw_sql, model_used = generate_sql(question)

    # Step 2 — SQL Validation Layer
    safe_sql = validate_and_sanitize(raw_sql)

    # Step 3 — Execute against Snowflake MARTS
    result = run_query(safe_sql)

    return QueryResponse(
        question=question,
        sql=safe_sql,
        model_used=model_used,
        columns=result["columns"],
        rows=result["rows"],
        row_count=result["row_count"],
    )
