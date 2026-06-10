"""
Risk Classifier — multi-factor risk assessment combining anomaly, RUL, and history.
"""
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EQUIPMENT, LOGS_DIR
from utils.logger import get_logger

log = get_logger("analytics.risk")

CRITICALITY_WEIGHT = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}


def classify_risk(
    equipment_id: str,
    anomaly_score: float = 0.0,
    anomaly_rate: float = 0.0,
    rul_hours: float = 1000.0,
) -> dict:
    """Classify risk level for equipment based on multiple factors."""
    info = EQUIPMENT.get(equipment_id, {})
    criticality = info.get("criticality", "medium")
    crit_w = CRITICALITY_WEIGHT.get(criticality, 0.5)

    # Historical failure frequency
    failure_freq = _get_failure_frequency(equipment_id)

    # Risk score components (0-1 each)
    anomaly_risk = min(1.0, anomaly_score * 2)
    rul_risk = max(0, 1.0 - rul_hours / 1000) if rul_hours is not None else 0.5
    history_risk = min(1.0, failure_freq / 20)

    # Weighted composite score
    risk_score = (
        anomaly_risk * 0.30
        + anomaly_rate * 0.15
        + rul_risk * 0.30
        + history_risk * 0.10
        + crit_w * 0.15
    )

    # Classification
    if risk_score >= 0.75:
        level, urgency = "critical", "Immediate intervention required"
    elif risk_score >= 0.50:
        level, urgency = "high", "Schedule maintenance within 24 hours"
    elif risk_score >= 0.30:
        level, urgency = "medium", "Plan maintenance within 1 week"
    else:
        level, urgency = "low", "Continue monitoring"

    return {
        "equipment_id": equipment_id,
        "equipment_name": info.get("name", equipment_id),
        "risk_level": level,
        "risk_score": round(risk_score, 3),
        "urgency": urgency,
        "criticality": criticality,
        "breakdown": {
            "anomaly_risk": round(anomaly_risk, 3),
            "rul_risk": round(rul_risk, 3),
            "history_risk": round(history_risk, 3),
            "criticality_factor": round(crit_w, 3),
        },
    }


def _get_failure_frequency(equipment_id: str) -> int:
    """Count historical failures for equipment."""
    csv_path = LOGS_DIR / "maintenance_logs.csv"
    if not csv_path.exists():
        return 0
    try:
        df = pd.read_csv(csv_path)
        return int(df[df["equipment_id"] == equipment_id].shape[0])
    except Exception:
        return 0


def get_all_risk_levels() -> list[dict]:
    """Get risk classification for all equipment."""
    from analytics.anomaly_detector import get_detector
    from analytics.rul_predictor import get_predictor

    detector = get_detector()
    predictor = get_predictor()

    results = []
    for eid in EQUIPMENT:
        status = detector.get_current_status(eid)
        rul = predictor.predict(eid)
        risk = classify_risk(
            eid,
            anomaly_score=status.get("anomaly_score", 0),
            anomaly_rate=status.get("recent_anomaly_rate", 0),
            rul_hours=rul.get("rul_hours", 1000),
        )
        risk["rul_hours"] = rul.get("rul_hours")
        risk["rul_days"] = rul.get("rul_days")
        results.append(risk)

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results
