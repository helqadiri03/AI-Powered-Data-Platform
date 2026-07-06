import time
from fastapi import APIRouter, HTTPException
from schemas.rag import RAGRequest, RAGResponse
from rag.retriever import get_retriever
from rag.vector_store import get_vector_store
from rag.embeddings import get_embeddings
from rag.chain import get_rag_chain, format_docs
from rag.prompts import get_rag_prompt
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from metrics import (
    PINECONE_RETRIEVAL_DURATION,
    LLM_GENERATION_DURATION,
    RAG_REQUEST_TOTAL,
)

router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)

@router.post("", response_model=RAGResponse, summary="Query the Documentation Assistant")
def query_rag(request: RAGRequest):
    try:
        embeddings = get_embeddings()
        vector_store = get_vector_store(embeddings)
        retriever = get_retriever(vector_store)
        prompt = get_rag_prompt()
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

        # ── Step 1: Pinecone retrieval (timed separately) ──────────────────
        t0 = time.perf_counter()
        context_docs = retriever.invoke(request.question)
        PINECONE_RETRIEVAL_DURATION.observe(time.perf_counter() - t0)

        # ── Step 2: LLM generation (timed separately) ─────────────────────
        formatted_context = format_docs(context_docs)
        chain = prompt | llm | StrOutputParser()
        t1 = time.perf_counter()
        answer = chain.invoke({"context": formatted_context, "question": request.question})
        LLM_GENERATION_DURATION.observe(time.perf_counter() - t1)

        # Extract unique sources
        sources_set = {
            doc.metadata.get("source_file")
            for doc in context_docs
            if doc.metadata.get("source_file")
        }

        RAG_REQUEST_TOTAL.labels(status="success").inc()
        return RAGResponse(answer=answer, sources=list(sources_set))

    except Exception as e:
        RAG_REQUEST_TOTAL.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))
