from langchain_pinecone import PineconeVectorStore
from langchain_core.vectorstores import VectorStoreRetriever

def get_retriever(vector_store: PineconeVectorStore, k: int = 5) -> VectorStoreRetriever:
    """
    Get a retriever from the vector store for similarity search.
    """
    return vector_store.as_retriever(search_kwargs={"k": k})
