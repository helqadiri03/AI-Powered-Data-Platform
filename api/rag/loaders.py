import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document

def load_documents(docs_dir: str = "../docs") -> list[Document]:
    """
    Load all markdown files from the specified directory.
    """
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True,
    )
    docs = loader.load()
    
    # Optional: Enhance metadata with section/source if needed
    for doc in docs:
        filename = os.path.basename(doc.metadata.get("source", ""))
        doc.metadata["source_file"] = filename
        
    return docs
