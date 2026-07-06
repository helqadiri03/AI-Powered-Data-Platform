"""
Centralized Prometheus custom metrics for the AI E-Commerce platform.
Import this module in any router that needs to record timings.
"""

from prometheus_client import Histogram, Counter

# --- RAG Pipeline ---
PINECONE_RETRIEVAL_DURATION = Histogram(
    "pinecone_retrieval_duration_seconds",
    "Time spent retrieving documents from Pinecone vector store",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
)

LLM_GENERATION_DURATION = Histogram(
    "llm_generation_duration_seconds",
    "Time spent generating an answer with the Groq LLM",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

RAG_REQUEST_TOTAL = Counter(
    "rag_requests_total",
    "Total number of RAG queries",
    ["status"],  # labels: success | error
)

# --- Text-to-SQL Pipeline ---
SQL_GENERATION_DURATION = Histogram(
    "sql_generation_duration_seconds",
    "Time spent generating SQL from natural language (LLM call)",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

SQL_EXECUTION_DURATION = Histogram(
    "sql_execution_duration_seconds",
    "Time spent executing the generated SQL query on Snowflake",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

SQL_REQUEST_TOTAL = Counter(
    "sql_requests_total",
    "Total number of Text-to-SQL queries",
    ["status"],  # labels: success | error
)
