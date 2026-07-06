import os
import sys
import logging

from dotenv import load_dotenv

try:
    from api.rag.loaders import load_documents
    from api.rag.splitter import split_documents
    from api.rag.embeddings import get_embeddings
    from api.rag.vector_store import get_vector_store
except ModuleNotFoundError:
    from rag.loaders import load_documents
    from rag.splitter import split_documents
    from rag.embeddings import get_embeddings
    from rag.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_docs():
    # Load env variables (for PINECONE_API_KEY, OPENAI_API_KEY, PINECONE_INDEX)
    load_dotenv()
    
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs")
    logger.info(f"Loading documents from {docs_dir}")
    
    docs = load_documents(docs_dir)
    logger.info(f"Loaded {len(docs)} documents.")
    
    logger.info("Splitting documents...")
    chunks = split_documents(docs)
    logger.info(f"Split into {len(chunks)} chunks.")
    
    logger.info("Initializing vector store...")
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    
    logger.info("Uploading to Pinecone...")
    vector_store.add_documents(chunks)
    logger.info("Ingestion complete!")

if __name__ == "__main__":
    ingest_docs()
