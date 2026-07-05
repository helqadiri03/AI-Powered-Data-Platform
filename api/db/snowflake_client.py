"""
Snowflake connection client.

Uses snowflake-connector-python to execute SQL against the MARTS schema.
Connections are opened per-request (connection pooling not needed at this scale).
"""

from __future__ import annotations

import logging
from typing import Any

import snowflake.connector
from snowflake.connector import DictCursor

from config import settings

logger = logging.getLogger(__name__)


def _get_connection() -> snowflake.connector.SnowflakeConnection:
    """Open a new Snowflake connection using env-configured credentials."""
    return snowflake.connector.connect(
        account=settings.snowflake_account,
        user=settings.snowflake_user,
        password=settings.snowflake_password,
        warehouse=settings.snowflake_warehouse,
        database=settings.snowflake_database,
        schema=settings.marts_schema,
        role=settings.snowflake_role,
        session_parameters={"QUERY_TAG": "fastapi-text-to-sql"},
    )


def run_query(sql: str) -> dict[str, Any]:
    """
    Execute a validated SQL query against Snowflake MARTS.

    Returns:
        {
            "columns": ["col1", "col2", ...],
            "rows": [[val, val, ...], ...],
            "row_count": N
        }
    """
    logger.info("Executing SQL against Snowflake MARTS:\n%s", sql)

    conn = _get_connection()
    try:
        with conn.cursor(DictCursor) as cur:
            cur.execute(sql)
            raw_rows = cur.fetchall()  # list[dict]

            if not raw_rows:
                return {"columns": [], "rows": [], "row_count": 0}

            columns = list(raw_rows[0].keys())
            rows = [list(row.values()) for row in raw_rows]

            logger.info("Query returned %d rows", len(rows))
            return {"columns": columns, "rows": rows, "row_count": len(rows)}
    finally:
        conn.close()


def test_connection() -> bool:
    """Lightweight connectivity check used by /health endpoint."""
    try:
        conn = _get_connection()
        conn.cursor().execute("SELECT 1")
        conn.close()
        return True
    except Exception as exc:
        logger.warning("Snowflake connectivity check failed: %s", exc)
        return False
