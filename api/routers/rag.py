from fastapi import APIRouter, HTTPException
from schemas.rag import RAGRequest, RAGResponse
from rag.chain import get_rag_chain

router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)

@router.post("", response_model=RAGResponse, summary="Query the Documentation Assistant")
def query_rag(request: RAGRequest):
    try:
        chain = get_rag_chain()
        result = chain.invoke(request.question)
        
        answer = result.get("answer", "")
        # Extract unique sources
        context_docs = result.get("context", [])
        sources_set = set()
        for doc in context_docs:
            source = doc.metadata.get("source_file")
            if source:
                sources_set.add(source)
                
        return RAGResponse(
            answer=answer,
            sources=list(sources_set)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
