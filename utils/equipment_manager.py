"""
Equipment Manager — CRUD operations for the dynamic equipment registry.
Adding a machine generates its manual + synthetic sensor data automatically;
deleting a machine removes its associated generated files.
"""
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    EQUIPMENT_REGISTRY_FILE, DATA_DIR, MANUALS_DIR, SENSOR_DIR,
    SENSOR_PARAMS, SENSOR_RANGES,
)
from utils.logger import get_logger

log = get_logger("utils.equipment_manager")

VALID_TYPES = list(SENSOR_PARAMS.keys())  # Blast Furnace, BOF, Rolling Mill, Caster, Ladle Furnace
VALID_CRITICALITY = ["critical", "high", "medium", "low"]


def load_registry() -> dict:
    """Load the current equipment registry from disk."""
    if EQUIPMENT_REGISTRY_FILE.exists():
        with open(EQUIPMENT_REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_registry(registry: dict):
    """Persist the equipment registry to disk."""
    EQUIPMENT_REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EQUIPMENT_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    log.info(f"Saved equipment registry ({len(registry)} units)")


def add_equipment(eid: str, name: str, etype: str, criticality: str,
                   generate_files: bool = True) -> tuple[bool, str]:
    """
    Add a new equipment unit. Returns (success, message).
    Validates ID format and uniqueness, then optionally generates
    a manual and synthetic sensor data using existing templates.
    """
    eid = eid.strip().upper()
    if not eid:
        return False, "Equipment ID cannot be empty."

    registry = load_registry()
    if eid in registry:
        return False, f"Equipment ID '{eid}' already exists."

    if etype not in VALID_TYPES:
        return False, f"Unknown equipment type '{etype}'. Must be one of: {', '.join(VALID_TYPES)}"

    if criticality not in VALID_CRITICALITY:
        return False, f"Invalid criticality '{criticality}'. Must be one of: {', '.join(VALID_CRITICALITY)}"

    registry[eid] = {"name": name.strip(), "type": etype, "criticality": criticality}
    save_registry(registry)

    if generate_files:
        _generate_manual(eid, name, etype)
        _generate_sensor_data(eid, etype)

    log.info(f"Added equipment {eid} ({name}, {etype}, {criticality})")
    return True, f"Added '{eid}' — {name} ({etype}, {criticality} criticality)."


def update_equipment(eid: str, name: str = None, criticality: str = None) -> tuple[bool, str]:
    """Update name and/or criticality of an existing equipment unit (type is immutable)."""
    registry = load_registry()
    if eid not in registry:
        return False, f"Equipment '{eid}' not found."

    if name:
        registry[eid]["name"] = name.strip()
    if criticality:
        if criticality not in VALID_CRITICALITY:
            return False, f"Invalid criticality '{criticality}'."
        registry[eid]["criticality"] = criticality

    save_registry(registry)
    log.info(f"Updated equipment {eid}")
    return True, f"Updated '{eid}'."


def delete_equipment(eid: str, delete_files: bool = True) -> tuple[bool, str]:
    """Remove an equipment unit from the registry and optionally delete its generated files."""
    registry = load_registry()
    if eid not in registry:
        return False, f"Equipment '{eid}' not found."

    del registry[eid]
    save_registry(registry)

    if delete_files:
        manual_path = MANUALS_DIR / f"{eid}_manual.md"
        sensor_path = SENSOR_DIR / f"{eid}_sensors.csv"
        for p in (manual_path, sensor_path):
            if p.exists():
                p.unlink()
                log.info(f"Deleted {p}")

    log.info(f"Deleted equipment {eid}")
    return True, f"Deleted '{eid}' and its generated files."


def _generate_manual(eid: str, name: str, etype: str):
    """Generate an equipment manual from the existing template for this type."""
    from utils.data_generator import MANUAL_TEMPLATES
    template = MANUAL_TEMPLATES.get(etype)
    if not template:
        log.warning(f"No manual template for type '{etype}', skipping manual generation")
        return
    content = template.format(eid=eid, name=name)
    MANUALS_DIR.mkdir(parents=True, exist_ok=True)
    path = MANUALS_DIR / f"{eid}_manual.md"
    path.write_text(content, encoding="utf-8")
    log.info(f"Generated manual for {eid}")


def _generate_sensor_data(eid: str, etype: str):
    """Generate synthetic sensor time-series for a new equipment unit."""
    import numpy as np
    import pandas as pd

    params = SENSOR_PARAMS.get(etype, [])
    ranges = SENSOR_RANGES.get(etype, {})
    if not params:
        log.warning(f"No sensor params for type '{etype}', skipping sensor data")
        return

    n_points = 2000
    timestamps = pd.date_range("2024-06-01", periods=n_points, freq="15min")
    data = {"timestamp": timestamps, "equipment_id": eid}
    for p in params:
        mean, std = ranges.get(p, (100, 10))
        values = np.random.normal(mean, std, n_points)
        anomaly_idx = np.random.choice(n_points, size=int(n_points * 0.05), replace=False)
        values[anomaly_idx] += np.random.choice([-1, 1], size=len(anomaly_idx)) * std * np.random.uniform(3, 6, len(anomaly_idx))
        degradation_start = int(n_points * 0.8)
        trend = np.linspace(0, std * 2, n_points - degradation_start)
        values[degradation_start:] += trend
        data[p] = np.round(values, 2)

    df = pd.DataFrame(data)
    SENSOR_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SENSOR_DIR / f"{eid}_sensors.csv", index=False)
    log.info(f"Generated sensor data for {eid}")


def reindex_manual(eid: str):
    """Re-index a single equipment's manual into ChromaDB (after add)."""
    from rag.document_loader import chunk_documents
    from rag.vector_store import index_documents
    from langchain_core.documents import Document

    path = MANUALS_DIR / f"{eid}_manual.md"
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    doc = Document(page_content=text, metadata={"source": str(path), "doc_type": "manual", "equipment_id": eid})
    chunks = chunk_documents([doc])
    index_documents(chunks)
    log.info(f"Re-indexed manual for {eid} ({len(chunks)} chunks)")
    return len(chunks)