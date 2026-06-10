"""
Embedding wrapper — uses HuggingFace sentence-transformers.
"""
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_MODEL
from utils.logger import get_logger

log = get_logger("rag.embeddings")

_embedding_instance = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the singleton embedding model."""
    global _embedding_instance
    if _embedding_instance is None:
        log.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
        )
        log.info("Embedding model loaded")
    return _embedding_instance
