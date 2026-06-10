"""
Feedback loop — SQLite-backed user feedback storage for continuous improvement.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import FEEDBACK_DB
from utils.logger import get_logger

log = get_logger("utils.feedback")


def _get_conn():
    conn = sqlite3.connect(str(FEEDBACK_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            intent TEXT,
            equipment_id TEXT,
            response TEXT,
            rating INTEGER,  -- 1=thumbs up, -1=thumbs down
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save_feedback(query: str, intent: str, equipment_id: str,
                  response: str, rating: int, comment: str = "") -> None:
    """Save user feedback on a response."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO feedback (timestamp, query, intent, equipment_id, response, rating, comment) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), query, intent, equipment_id or "", response[:2000], rating, comment),
    )
    conn.commit()
    conn.close()
    log.info(f"Feedback saved: {'positive' if rating > 0 else 'negative'}")


def get_feedback_stats() -> dict:
    """Get feedback statistics."""
    conn = _get_conn()
    cur = conn.execute("SELECT COUNT(*), SUM(CASE WHEN rating > 0 THEN 1 ELSE 0 END) FROM feedback")
    total, positive = cur.fetchone()
    conn.close()
    total = total or 0
    positive = positive or 0
    return {
        "total": total,
        "positive": positive,
        "negative": total - positive,
        "satisfaction_rate": round(positive / total * 100, 1) if total > 0 else 0,
    }
