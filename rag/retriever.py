"""
Retriever — multi-collection retrieval with source citation tracking.
"""
from pathlib import Path
from typing import Optional
from langchain_core.documents import Document

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TOP_K_RETRIEVAL
from rag.vector_store import get_or_create_vectorstore
from utils.logger import get_logger

log = get_logger("rag.retriever")


def retrieve(
    query: str,
    collection_name: str = "maintenance_knowledge",
    top_k: int = TOP_K_RETRIEVAL,
    filter_metadata: Optional[dict] = None,
) -> list[Document]:
    """Retrieve relevant documents for a query."""
    vs = get_or_create_vectorstore(collection_name)
    kwargs = {"k": top_k}
    if filter_metadata:
        kwargs["filter"] = filter_metadata
    results = vs.similarity_search(query, **kwargs)
    log.info(f"Retrieved {len(results)} docs for query: '{query[:60]}...'")
    return results


def retrieve_with_scores(
    query: str,
    collection_name: str = "maintenance_knowledge",
    top_k: int = TOP_K_RETRIEVAL,
) -> list[tuple[Document, float]]:
    """Retrieve documents with relevance scores."""
    vs = get_or_create_vectorstore(collection_name)
    results = vs.similarity_search_with_relevance_scores(query, k=top_k)
    return results


def format_context(docs: list[Document], max_chars: int = 6000) -> str:
    """Format retrieved documents into a context string for the LLM."""
    parts = []
    total = 0
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        doc_type = doc.metadata.get("doc_type", "unknown")
        header = f"[Source {i+1}: {doc_type} — {Path(source).name}]"
        snippet = doc.page_content
        if total + len(snippet) > max_chars:
            snippet = snippet[:max_chars - total]
        parts.append(f"{header}\n{snippet}")
        total += len(snippet)
        if total >= max_chars:
            break
    return "\n\n---\n\n".join(parts)


def get_source_citations(docs: list[Document]) -> list[str]:
    """Extract source citations from retrieved documents."""
    citations = []
    for doc in docs:
        source = Path(doc.metadata.get("source", "unknown")).name
        doc_type = doc.metadata.get("doc_type", "unknown")
        eid = doc.metadata.get("equipment_id", "")
        citation = f"{doc_type}: {source}"
        if eid:
            citation += f" (Equipment: {eid})"
        citations.append(citation)
    return list(set(citations))
