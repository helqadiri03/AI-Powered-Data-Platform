"""
FastAPI application entry point.

Exposes:
  GET  /health         → liveness probe
  POST /api/query      → NL → SQL → Snowflake
  GET  /docs           → Swagger UI (auto-generated)
  GET  /redoc          → ReDoc UI
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.snowflake_client import test_connection
from routers.query import router as query_router
from routers.rag import router as rag_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="AI-Powered E-Commerce Analytics API",
    description=(
        "Text-to-SQL agent that translates natural-language questions "
        "into Snowflake SQL queries against the MARTS analytics layer."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow React dev server and any same-origin production origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
        "http://localhost:8080",   # Airflow (internal)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(query_router)
app.include_router(rag_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Liveness & Snowflake connectivity probe")
def health() -> dict:
    snowflake_ok = test_connection()
    return {
        "status": "ok",
        "snowflake": "connected" if snowflake_ok else "unreachable",
    }
