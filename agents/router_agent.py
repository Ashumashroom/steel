"""
Router Agent — classifies user intent and extracts equipment ID.
"""
import re, json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from config import get_equipment
from utils.logger import get_logger

log = get_logger("agents.router")

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for a steel plant maintenance system.
Given a user query, classify it into exactly ONE of these intents:
- "diagnosis" — user describes a fault, symptom, error, or asks what's wrong
- "rca" — user asks for root cause analysis of a failure or incident
- "prediction" — user asks about equipment health, remaining life, predictions, or anomalies
- "planning" — user asks for maintenance plan, schedule, spare parts, or recommendations
- "general" — general question about equipment, processes, or procedures

Also extract the equipment_id if mentioned (e.g., BF-001, BOF-002, RM-003, CC-001, LF-001).

Respond in JSON format ONLY:
{"intent": "...", "equipment_id": "..." or null}
"""


def _build_equipment_aliases(equipment: dict) -> dict:
    """Build an alias map fresh from the current equipment registry."""
    aliases = {}
    for eid, info in equipment.items():
        name_lower = info["name"].lower()
        aliases[eid.lower()] = eid
        aliases[name_lower] = eid
        for word in name_lower.split():
            if len(word) > 3:
                aliases[word] = eid
    return aliases


def _extract_equipment_id(query: str) -> str | None:
    """Extract equipment ID from query using regex and aliases."""
    equipment = get_equipment()

    # Direct ID pattern (e.g., BF-001, RM-003)
    match = re.search(r'\b([A-Z]{2,3}-\d{3})\b', query.upper())
    if match:
        eid = match.group(1)
        if eid in equipment:
            return eid

    # Check aliases (rebuilt from current registry each call)
    query_lower = query.lower()
    aliases = _build_equipment_aliases(equipment)
    for alias, eid in aliases.items():
        if alias in query_lower:
            return eid
    return None


def router_node(state: MaintenanceState) -> dict:
    """LangGraph node: classify intent and route query."""
    query = state["user_query"]
    log.info(f"Routing query: '{query[:80]}...'")

    # Extract equipment ID locally first
    equipment_id = _extract_equipment_id(query)

    # Use LLM for intent classification
    try:
        response = call_llm(query, ROUTER_SYSTEM_PROMPT, use_router_model=True)
        # Parse JSON from response
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            parsed = json.loads(json_match.group())
            intent = parsed.get("intent", "general")
            if not equipment_id and parsed.get("equipment_id"):
                equipment_id = parsed["equipment_id"]
        else:
            intent = _fallback_intent(query)
    except Exception as e:
        log.warning(f"LLM routing failed: {e}, using fallback")
        intent = _fallback_intent(query)

    valid_intents = {"diagnosis", "rca", "prediction", "planning", "general"}
    if intent not in valid_intents:
        intent = "general"

    log.info(f"Routed to: {intent} | Equipment: {equipment_id}")
    return {"intent": intent, "equipment_id": equipment_id}


def _fallback_intent(query: str) -> str:
    """Rule-based fallback for intent classification."""
    q = query.lower()
    if any(w in q for w in ["diagnos", "fault", "error", "wrong", "issue", "problem", "symptom", "vibrat"]):
        return "diagnosis"
    elif any(w in q for w in ["root cause", "rca", "why", "failure analysis", "investigate"]):
        return "rca"
    elif any(w in q for w in ["predict", "rul", "remaining", "health", "anomal", "forecast", "life"]):
        return "prediction"
    elif any(w in q for w in ["plan", "schedule", "maintenan", "repair", "spare", "recommend", "action"]):
        return "planning"
    return "general"