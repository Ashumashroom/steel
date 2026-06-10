"""
Document loader — loads and chunks equipment manuals, SOPs, logs, and failure reports.
"""
import os
from pathlib import Path
from typing import Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    MANUALS_DIR, SOPS_DIR, LOGS_DIR, SENSOR_DIR, SPARE_PARTS_DIR,
    CHUNK_SIZE, CHUNK_OVERLAP,
)
from utils.logger import get_logger

log = get_logger("rag.loader")


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_manuals() -> list[Document]:
    """Load equipment manuals as LangChain Documents."""
    docs = []
    if not MANUALS_DIR.exists():
        log.warning("Manuals directory not found")
        return docs
    for f in MANUALS_DIR.glob("*.md"):
        eid = f.stem.replace("_manual", "")
        text = _read_text_file(f)
        docs.append(Document(
            page_content=text,
            metadata={"source": str(f), "doc_type": "manual", "equipment_id": eid},
        ))
    log.info(f"Loaded {len(docs)} equipment manuals")
    return docs


def load_sops() -> list[Document]:
    """Load SOPs as LangChain Documents."""
    docs = []
    if not SOPS_DIR.exists():
        return docs
    for f in SOPS_DIR.glob("*.md"):
        text = _read_text_file(f)
        docs.append(Document(
            page_content=text,
            metadata={"source": str(f), "doc_type": "sop", "equipment_id": "ALL"},
        ))
    log.info(f"Loaded {len(docs)} SOPs")
    return docs


def load_failure_reports() -> list[Document]:
    """Load failure analysis reports."""
    docs = []
    if not LOGS_DIR.exists():
        return docs
    for f in LOGS_DIR.glob("failure_report_*.md"):
        text = _read_text_file(f)
        docs.append(Document(
            page_content=text,
            metadata={"source": str(f), "doc_type": "failure_report"},
        ))
    log.info(f"Loaded {len(docs)} failure reports")
    return docs


def load_maintenance_logs() -> list[Document]:
    """Load maintenance logs CSV as chunked text documents."""
    docs = []
    csv_path = LOGS_DIR / "maintenance_logs.csv"
    if not csv_path.exists():
        return docs
    import pandas as pd
    df = pd.read_csv(csv_path)
    # Group by equipment for better retrieval
    for eid, group in df.groupby("equipment_id"):
        lines = []
        for _, row in group.iterrows():
            lines.append(
                f"[{row['timestamp']}] {eid} | {row['fault_code']} | "
                f"{row['description']} | Severity: {row['severity']} | "
                f"Action: {row['action_taken']} | Downtime: {row['downtime_hours']}h"
            )
        text = "\n".join(lines)
        docs.append(Document(
            page_content=text,
            metadata={"source": str(csv_path), "doc_type": "maintenance_log", "equipment_id": eid},
        ))
    log.info(f"Loaded maintenance logs for {len(docs)} equipment units")
    return docs


def load_spare_parts() -> list[Document]:
    """Load spare parts inventory as a document."""
    csv_path = SPARE_PARTS_DIR / "spare_parts_inventory.csv"
    if not csv_path.exists():
        return []
    import pandas as pd
    df = pd.read_csv(csv_path)
    lines = ["# Spare Parts Inventory\n"]
    for _, row in df.iterrows():
        lines.append(
            f"- **{row['part_name']}** (ID: {row['part_id']}): "
            f"Equipment {row['equipment_id']}, Stock: {row['quantity_in_stock']}, "
            f"Lead time: {row['lead_time_days']} days, "
            f"Cost: INR {row['unit_cost_inr']:,.0f}, Supplier: {row['supplier']}"
        )
    text = "\n".join(lines)
    return [Document(
        page_content=text,
        metadata={"source": str(csv_path), "doc_type": "spare_parts"},
    )]


def load_all_documents() -> list[Document]:
    """Load all document types."""
    all_docs = []
    all_docs.extend(load_manuals())
    all_docs.extend(load_sops())
    all_docs.extend(load_failure_reports())
    all_docs.extend(load_maintenance_logs())
    all_docs.extend(load_spare_parts())
    log.info(f"Total documents loaded: {len(all_docs)}")
    return all_docs


def chunk_documents(docs: list[Document], chunk_size: int = CHUNK_SIZE,
                    chunk_overlap: int = CHUNK_OVERLAP) -> list[Document]:
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)
    log.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
    return chunks
