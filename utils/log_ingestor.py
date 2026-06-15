"""
Log Ingestor — parses uploaded free-text/CSV log files, auto-detects which
equipment and which agent/category each entry belongs to, and merges new
entries into the maintenance logs CSV for RAG re-indexing.
"""
import re
import io
import csv
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EQUIPMENT, LOGS_DIR
from utils.logger import get_logger

log = get_logger("utils.log_ingestor")

MAINT_LOG_CSV = LOGS_DIR / "maintenance_logs.csv"
CSV_COLUMNS = ["timestamp", "equipment_id", "fault_code", "description",
               "severity", "action_taken", "downtime_hours", "technician"]

# ──────────────────────────────────────────────
# Equipment alias map (built once from EQUIPMENT registry)
# ──────────────────────────────────────────────
_EQUIPMENT_ALIASES: dict[str, str] = {}
for _eid, _info in EQUIPMENT.items():
    _EQUIPMENT_ALIASES[_eid.lower()] = _eid
    _EQUIPMENT_ALIASES[_info["name"].lower()] = _eid
    for _word in _info["name"].lower().split():
        if len(_word) > 3:
            _EQUIPMENT_ALIASES.setdefault(_word, _eid)
    for _word in _info["type"].lower().split():
        if len(_word) > 3:
            _EQUIPMENT_ALIASES.setdefault(_word, _eid)

# ──────────────────────────────────────────────
# Agent / category keyword map — mirrors router_agent.py logic
# ──────────────────────────────────────────────
AGENT_KEYWORDS = {
    "diagnosis": ["diagnos", "fault", "error", "wrong", "issue", "problem",
                  "symptom", "vibrat", "alarm", "trip", "abnormal"],
    "rca": ["root cause", "rca", "investigate", "failure analysis",
            "why", "incident"],
    "prediction": ["predict", "rul", "remaining", "health", "anomal",
                   "forecast", "life", "degrad", "trend"],
    "planning": ["plan", "schedule", "maintenan", "repair", "spare",
                  "recommend", "action", "replace", "overhaul", "pm "],
}

SEVERITY_KEYWORDS = {
    "critical": ["critical", "emergency", "shutdown", "catastroph", "failure", "down"],
    "high": ["high", "severe", "major", "urgent"],
    "medium": ["medium", "moderate", "warning"],
    "low": ["low", "minor", "info"],
}

FAULT_CODE_RE = re.compile(r"\b([A-Z]{2,4}-F\d{3,4})\b")
EQUIPMENT_ID_RE = re.compile(r"\b([A-Z]{2,3}-\d{3})\b")
DOWNTIME_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hours)\b", re.I)
TECH_RE = re.compile(r"\b(Tech-\d+|technician[: ]+\S+)", re.I)


def extract_equipment_id(text: str) -> str | None:
    """Find an equipment ID via direct ID pattern or alias matching."""
    match = EQUIPMENT_ID_RE.search(text.upper())
    if match and match.group(1) in EQUIPMENT:
        return match.group(1)

    text_lower = text.lower()
    for alias, eid in _EQUIPMENT_ALIASES.items():
        if alias in text_lower:
            return eid
    return None


def classify_agent(text: str) -> str:
    """Classify which agent/category this log line is most relevant to."""
    text_lower = text.lower()
    scores = {agent: 0 for agent in AGENT_KEYWORDS}
    for agent, keywords in AGENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[agent] += 1
    best_agent = max(scores, key=scores.get)
    if scores[best_agent] == 0:
        return "general"
    return best_agent


def classify_severity(text: str) -> str:
    """Best-effort severity classification from free text."""
    text_lower = text.lower()
    for level, keywords in SEVERITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return "medium"


def parse_log_line(line: str) -> dict | None:
    """
    Parse a single free-text log line into a structured maintenance log entry.
    Returns None if the line is empty/unparseable (e.g. blank or header-only).
    """
    line = line.strip()
    if not line:
        return None

    equipment_id = extract_equipment_id(line)
    if not equipment_id:
        return None  # Skip lines we can't attribute to any known equipment

    agent = classify_agent(line)
    severity = classify_severity(line)

    fault_match = FAULT_CODE_RE.search(line.upper())
    fault_code = fault_match.group(1) if fault_match else f"EXT-{equipment_id}-{abs(hash(line)) % 1000:03d}"

    downtime_match = DOWNTIME_RE.search(line)
    downtime_hours = float(downtime_match.group(1)) if downtime_match else 0.0

    tech_match = TECH_RE.search(line)
    technician = tech_match.group(1) if tech_match else "Uploaded-Log"

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "equipment_id": equipment_id,
        "fault_code": fault_code,
        "description": line[:250],
        "severity": severity,
        "action_taken": "(from uploaded log — pending review)",
        "downtime_hours": downtime_hours,
        "technician": technician,
        "_agent": agent,  # extra field for UI preview, not written to CSV
    }


def parse_log_file(file_bytes: bytes, filename: str) -> list[dict]:
    """
    Parse an uploaded log file (txt or csv) into a list of structured entries.
    """
    text = file_bytes.decode("utf-8", errors="replace")
    entries = []

    if filename.lower().endswith(".csv"):
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            # Build a single text blob from the row for classification
            blob = " | ".join(f"{k}: {v}" for k, v in row.items())
            parsed = parse_log_line(blob)
            if parsed:
                # Prefer explicit CSV fields where present
                for col in CSV_COLUMNS:
                    if col in row and row[col]:
                        if col == "downtime_hours":
                            try:
                                parsed[col] = float(row[col])
                            except ValueError:
                                pass
                        else:
                            parsed[col] = row[col]
                entries.append(parsed)
    else:
        for line in text.splitlines():
            parsed = parse_log_line(line)
            if parsed:
                entries.append(parsed)

    log.info(f"Parsed {len(entries)} entries from uploaded file '{filename}'")
    return entries


def commit_entries(entries: list[dict]) -> int:
    """
    Append parsed entries to maintenance_logs.csv (creating it if needed).
    Returns the number of rows written.
    """
    import pandas as pd

    rows = []
    for e in entries:
        row = {col: e.get(col, "") for col in CSV_COLUMNS}
        rows.append(row)

    new_df = pd.DataFrame(rows, columns=CSV_COLUMNS)

    if MAINT_LOG_CSV.exists():
        existing_df = pd.read_csv(MAINT_LOG_CSV)
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        MAINT_LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
        combined = new_df

    combined.to_csv(MAINT_LOG_CSV, index=False)
    log.info(f"Committed {len(rows)} new log entries to {MAINT_LOG_CSV}")
    return len(rows)


def reindex_logs():
    """Re-run RAG indexing for maintenance logs after new entries are committed."""
    from rag.document_loader import load_maintenance_logs, chunk_documents
    from rag.vector_store import index_documents

    docs = load_maintenance_logs()
    chunks = chunk_documents(docs)
    index_documents(chunks)
    log.info(f"Re-indexed {len(chunks)} maintenance log chunks")
    return len(chunks)