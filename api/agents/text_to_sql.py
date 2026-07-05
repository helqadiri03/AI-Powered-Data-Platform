"""
Text-to-SQL Agent.

Uses Groq (llama-3.3-70b-versatile with llama-3.1-8b-instant fallback)
to translate a natural-language question into a Snowflake SQL SELECT statement
against the ECOMMERCE_DB.MARTS schema.
"""

from __future__ import annotations

import logging
import re

from groq import Groq, APIError, RateLimitError
from fastapi import HTTPException

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema context injected into every LLM prompt
# ---------------------------------------------------------------------------
SCHEMA_CONTEXT = """
You have access to a Snowflake data warehouse named ECOMMERCE_DB, schema MARTS.
The available tables and their columns are:

1. FACT_SALES
   - order_id          VARCHAR   (unique order identifier)
   - order_item_id     VARCHAR   (line-item identifier within an order)
   - product_id        VARCHAR   (FK → DIM_PRODUCT)
   - customer_id       VARCHAR   (FK → DIM_CUSTOMER)
   - order_timestamp   TIMESTAMP (full purchase datetime)
   - order_date        DATE      (purchase date, FK → DIM_DATE.date_day)
   - price             FLOAT     (item selling price in BRL)
   - freight_value     FLOAT     (shipping cost in BRL)
   - order_status      VARCHAR   (e.g. delivered, shipped, canceled)

2. FACT_MARKETING
   - campaign_id       VARCHAR   (FK → DIM_CAMPAIGN)
   - performance_date  DATE      (date of the performance record)
   - platform          VARCHAR   (e.g. google, facebook, instagram)
   - spend             FLOAT     (ad spend in USD)
   - impressions       INTEGER   (number of ad impressions)
   - clicks            INTEGER   (number of clicks)
   - conversions       INTEGER   (number of conversions)
   - revenue           FLOAT     (attributed revenue in USD)

3. DIM_CUSTOMER
   - customer_id              VARCHAR  (PK)
   - customer_unique_id       VARCHAR  (de-duplicated customer key)
   - customer_city            VARCHAR
   - customer_state           VARCHAR  (2-letter BR state code)
   - customer_zip_code_prefix VARCHAR

4. DIM_PRODUCT
   - product_id              VARCHAR  (PK)
   - product_category_name   VARCHAR  (product category in Portuguese)
   - product_weight_g        FLOAT
   - product_length_cm       FLOAT
   - product_height_cm       FLOAT
   - product_width_cm        FLOAT

5. DIM_CAMPAIGN
   - campaign_id    VARCHAR  (PK)
   - campaign_name  VARCHAR
   - category       VARCHAR  (product category targeted)
   - platform       VARCHAR
   - objective      VARCHAR  (e.g. awareness, conversions, traffic)
   - status         VARCHAR  (active, paused, completed)
   - total_budget   FLOAT    (total campaign budget in USD)
   - start_date     DATE
   - end_date       DATE

6. DIM_DATE
   - date_day   DATE     (PK)
   - year       INTEGER
   - month      INTEGER  (1–12)
   - day        INTEGER  (1–31)
   - quarter    INTEGER  (1–4)
   - day_name   VARCHAR  (e.g. Mon, Tue)
""".strip()

SYSTEM_PROMPT = f"""
You are an expert Snowflake SQL generator for an e-commerce analytics platform.

{SCHEMA_CONTEXT}

Rules you MUST follow:
- Generate ONLY valid Snowflake SQL SELECT statements. No DML, DDL, or procedural code.
- Always qualify table names without a schema prefix (the API sets the schema context).
- Use meaningful column aliases when aggregating.
- Prefer JOINs over subqueries for readability.
- Output ONLY the raw SQL — no markdown, no explanation, no code fences.
- Do not include a LIMIT clause; the API enforces one automatically.
""".strip()


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

_client = Groq(api_key=settings.groq_api_key)


def _call_groq(question: str, model: str) -> str:
    """Call Groq chat completion and return the SQL text."""
    response = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {question}"},
        ],
        temperature=0.0,       # deterministic SQL
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def _clean_sql(raw: str) -> str:
    """Strip any accidental markdown fences the model might emit."""
    raw = re.sub(r"^```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def generate_sql(question: str) -> tuple[str, str]:
    """
    Translate a natural-language question to SQL.

    Returns:
        (sql: str, model_used: str)

    Tries the primary model first; falls back to the secondary on rate-limit
    or API errors.
    """
    for model in (settings.groq_model_primary, settings.groq_model_fallback):
        try:
            logger.info("Calling Groq model '%s' for question: %s", model, question)
            raw = _call_groq(question, model)
            sql = _clean_sql(raw)
            logger.info("Generated SQL (%s):\n%s", model, sql)
            return sql, model
        except RateLimitError:
            logger.warning("Rate limit hit on model '%s', trying fallback.", model)
            continue
        except APIError as exc:
            logger.warning("API error on model '%s': %s — trying fallback.", model, exc)
            continue

    raise HTTPException(
        status_code=503,
        detail="All Groq models are currently unavailable. Please try again later.",
    )
