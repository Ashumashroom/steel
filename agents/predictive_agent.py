"""
Predictive Agent — anomaly detection + RUL prediction integration.
"""
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from analytics.anomaly_detector import get_detector
from analytics.rul_predictor import get_predictor
from analytics.risk_classifier import classify_risk, get_all_risk_levels
from config import EQUIPMENT
from utils.logger import get_logger

log = get_logger("agents.predictive")

PRED_SYSTEM_PROMPT = """You are a predictive maintenance expert for steel manufacturing.
Using the anomaly detection results, RUL predictions, and risk assessments provided,
generate a clear, actionable predictive maintenance report.

Include:
1. **Current Equipment Status**: Health summary based on analytics
2. **Anomaly Detection Results**: What abnormalities were found
3. **Remaining Useful Life (RUL)**: Time until expected failure
4. **Risk Assessment**: Risk level with justification
5. **Early Warnings**: Potential catastrophic failure risks
6. **Recommended Actions**: Prioritized by urgency

Use the analytics data provided — do NOT invent sensor readings."""


def predictive_node(state: MaintenanceState) -> dict:
    """LangGraph node: run predictive analytics and generate report."""
    query = state["user_query"]
    equipment_id = state.get("equipment_id")

    log.info(f"Predictive analysis: {query[:60]}...")

    detector = get_detector()
    predictor = get_predictor()
    alerts = []

    if equipment_id and equipment_id in EQUIPMENT:
        # Single equipment analysis
        anomaly_status = detector.get_current_status(equipment_id)
        rul_result = predictor.predict(equipment_id)
        risk = classify_risk(
            equipment_id,
            anomaly_score=anomaly_status.get("anomaly_score", 0),
            anomaly_rate=anomaly_status.get("recent_anomaly_rate", 0),
            rul_hours=rul_result.get("rul_hours", 1000),
        )

        analytics_summary = f"""### Analytics Results for {EQUIPMENT[equipment_id]['name']} ({equipment_id})

**Anomaly Detection:**
- Current Status: {anomaly_status['status'].upper()}
- Anomaly Score: {anomaly_status.get('anomaly_score', 0):.3f}
- Recent Anomaly Rate: {anomaly_status.get('recent_anomaly_rate', 0):.1%}

**Remaining Useful Life:**
- Estimated RUL: {rul_result.get('rul_hours', 'N/A')} hours ({rul_result.get('rul_days', 'N/A')} days)
- Confidence: {rul_result.get('confidence', 'N/A')}
- Status: {rul_result.get('status', 'N/A')}

**Risk Assessment:**
- Risk Level: {risk['risk_level'].upper()}
- Risk Score: {risk['risk_score']:.3f}
- Urgency: {risk['urgency']}
"""
        predictions = {"anomaly": anomaly_status, "rul": rul_result, "risk": risk}

        if risk["risk_level"] in ("critical", "high"):
            alerts.append({
                "equipment_id": equipment_id,
                "severity": risk["risk_level"],
                "message": f"{EQUIPMENT[equipment_id]['name']}: {risk['urgency']}",
            })
    else:
        # All equipment overview
        all_risks = get_all_risk_levels()
        lines = ["### Fleet-Wide Equipment Health Overview\n"]
        for r in all_risks:
            eid = r["equipment_id"]
            lines.append(
                f"| {eid} | {r['equipment_name']} | {r['risk_level'].upper()} | "
                f"RUL: {r.get('rul_days', 'N/A')} days | {r['urgency']} |"
            )
            if r["risk_level"] in ("critical", "high"):
                alerts.append({
                    "equipment_id": eid,
                    "severity": r["risk_level"],
                    "message": f"{r['equipment_name']}: {r['urgency']}",
                })
        analytics_summary = "\n".join(lines)
        predictions = {"all_risks": all_risks}

    prompt = f"""## User Query
{query}

## Analytics Data
{analytics_summary}

Generate a comprehensive predictive maintenance report:"""

    response = call_llm(prompt, PRED_SYSTEM_PROMPT)

    return {
        "predictions": predictions,
        "final_response": response,
        "alerts": alerts,
        "risk_assessment": predictions.get("risk", {}),
    }
