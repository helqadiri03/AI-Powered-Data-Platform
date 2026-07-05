"""
SQL Validation Layer.

Protects Snowflake from destructive or out-of-scope queries:
  1. Only SELECT statements are permitted.
  2. Only MARTS tables can be referenced.
  3. A hard LIMIT is injected/enforced to cap result size.
"""

from __future__ import annotations

import logging
import re

import sqlglot
import sqlglot.expressions as exp
from fastapi import HTTPException

from config import settings

logger = logging.getLogger(__name__)

# Exact set of tables exposed through the API
ALLOWED_TABLES: set[str] = {
    "FACT_SALES",
    "FACT_MARKETING",
    "DIM_CUSTOMER",
    "DIM_PRODUCT",
    "DIM_CAMPAIGN",
    "DIM_DATE",
}

# Keywords that must never appear in the final SQL
FORBIDDEN_KEYWORDS: list[str] = [
    "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
    "TRUNCATE", "MERGE", "GRANT", "REVOKE", "EXECUTE", "CALL",
]


def _parse(sql: str) -> sqlglot.Expression:
    """Parse SQL with sqlglot; raise 400 on syntax errors."""
    try:
        parsed = sqlglot.parse_one(sql, dialect="snowflake")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SQL parse error: {exc}") from exc
    if parsed is None:
        raise HTTPException(status_code=400, detail="Empty or unparseable SQL.")
    return parsed


def _assert_select_only(parsed: sqlglot.Expression) -> None:
    """Reject anything that is not a plain SELECT."""
    if not isinstance(parsed, exp.Select):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT statements are permitted.",
        )


def _assert_no_forbidden_keywords(sql: str) -> None:
    """Catch forbidden keywords via a fast regex scan on the raw SQL."""
    upper = sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        # word-boundary match to avoid false positives (e.g. 'CREATED_AT')
        if re.search(rf"\b{kw}\b", upper):
            raise HTTPException(
                status_code=400,
                detail=f"Forbidden keyword detected: {kw}",
            )


def _assert_allowed_tables(parsed: sqlglot.Expression) -> None:
    """Ensure every table reference is in ALLOWED_TABLES."""
    referenced = {
        table.name.upper()
        for table in parsed.find_all(exp.Table)
    }
    disallowed = referenced - ALLOWED_TABLES
    if disallowed:
        raise HTTPException(
            status_code=400,
            detail=f"Query references disallowed table(s): {', '.join(sorted(disallowed))}",
        )


def _inject_limit(sql: str, parsed: sqlglot.Expression) -> str:
    """
    Ensure the query has a LIMIT clause.
    If the model already provided one, cap it at settings.query_row_limit.
    If missing, append LIMIT.
    """
    limit_node = parsed.find(exp.Limit)
    max_limit = settings.query_row_limit

    if limit_node is not None:
        # Extract numeric value and cap it
        try:
            current = int(limit_node.expression.this)
            if current > max_limit:
                sql = re.sub(
                    r"\bLIMIT\s+\d+\b",
                    f"LIMIT {max_limit}",
                    sql,
                    flags=re.IGNORECASE,
                )
                logger.info("LIMIT capped from %d to %d", current, max_limit)
        except (ValueError, AttributeError):
            pass
    else:
        sql = sql.rstrip().rstrip(";") + f"\nLIMIT {max_limit}"
        logger.info("LIMIT %d appended to query.", max_limit)

    return sql


def validate_and_sanitize(sql: str) -> str:
    """
    Full validation pipeline. Returns a safe, sanitized SQL string
    or raises HTTPException(400) with a descriptive message.
    """
    sql = sql.strip()

    # 1. Fast keyword scan before parsing
    _assert_no_forbidden_keywords(sql)

    # 2. Parse
    parsed = _parse(sql)

    # 3. Must be SELECT
    _assert_select_only(parsed)

    # 4. Only MARTS tables
    _assert_allowed_tables(parsed)

    # 5. Enforce row limit
    sql = _inject_limit(sql, parsed)

    logger.info("SQL passed all validation checks.")
    return sql
