"""
ChromaDB vector store — persistent storage with metadata filtering.
"""
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHROMA_DIR
from rag.embeddings import get_embeddings
from utils.logger import get_logger

log = get_logger("rag.vectorstore")


def get_or_create_vectorstore(
    collection_name: str = "maintenance_knowledge",
) -> Chroma:
    """Get or create a ChromaDB vector store."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    log.info(f"Vector store ready: {collection_name} ({vectorstore._collection.count()} docs)")
    return vectorstore


def index_documents(
    documents: list[Document],
    collection_name: str = "maintenance_knowledge",
) -> Chroma:
    """Index documents into ChromaDB."""
    if not documents:
        log.warning("No documents to index")
        return get_or_create_vectorstore(collection_name)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings()

    # Check if already indexed
    vs = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    existing_count = vs._collection.count()
    if existing_count > 0:
        log.info(f"Collection '{collection_name}' already has {existing_count} docs — skipping re-index")
        return vs

    log.info(f"Indexing {len(documents)} documents into '{collection_name}'...")
    vs = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(CHROMA_DIR),
    )
    log.info(f"Indexed {vs._collection.count()} chunks into '{collection_name}'")
    return vs
