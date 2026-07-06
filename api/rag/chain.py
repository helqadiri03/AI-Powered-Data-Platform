from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

from .embeddings import get_embeddings
from .vector_store import get_vector_store
from .retriever import get_retriever
from .prompts import get_rag_prompt

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(f"Source ({doc.metadata.get('source_file', 'unknown')}):\n{doc.page_content}" for doc in docs)

def get_rag_chain():
    """
    Build and return the RAG pipeline using Groq.
    """
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    retriever = get_retriever(vector_store)
    prompt = get_rag_prompt()
    
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
    
    from langchain_core.runnables import RunnableParallel
    
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )
    
    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    return rag_chain_with_source
