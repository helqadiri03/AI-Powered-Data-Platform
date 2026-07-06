import os
from langchain_pinecone import PineconeVectorStore
from langchain_core.embeddings import Embeddings

def get_vector_store(embeddings: Embeddings) -> PineconeVectorStore:
    """
    Initialize and return the Pinecone vector store.
    """
    index_name = os.environ.get("PINECONE_INDEX", "ecommerce-docs")
    
    # Requires PINECONE_API_KEY environment variable
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )
