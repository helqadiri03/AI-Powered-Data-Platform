from langchain_pinecone import PineconeEmbeddings
import os

def get_embeddings() -> PineconeEmbeddings:
    """
    Initialize and return the Pinecone embeddings model.
    Uses the free Pinecone Inference API to save local disk space.
    """
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    return PineconeEmbeddings(
        model="multilingual-e5-large",
        pinecone_api_key=pinecone_api_key
    )
