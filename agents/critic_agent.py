"""
Critic Agent — validates agent outputs for quality and completeness.
"""
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from config import MAX_REVISION_LOOPS
from utils.logger import get_logger

log = get_logger("agents.critic")

CRITIC_SYSTEM_PROMPT = """You are a quality reviewer for a steel plant maintenance AI system.
Evaluate the agent's response for:
1. **Completeness**: Does it address all aspects of the user's query?
2. **Accuracy**: Are the technical details correct based on the context provided?
3. **Actionability**: Are the recommendations specific enough to act on?
4. **Safety**: Are safety considerations addressed where relevant?
5. **Clarity**: Is the response well-structured and easy to understand?

Respond in JSON format:
{
    "approved": true/false,
    "score": 0.0-1.0,
    "feedback": "specific improvement suggestions if not approved"
}

Be strict but fair. Approve if the response is good enough for a maintenance engineer to act on.
Minor formatting issues should not cause rejection."""


def critic_node(state: MaintenanceState) -> dict:
    """LangGraph node: validate and optionally request revision."""
    intent = state.get("intent", "general")
    revision_count = state.get("revision_count", 0)

    # Get the agent output to review
    output = _get_agent_output(state)
    if not output:
        return {"is_validated": True, "final_response": "No output to validate."}

    # Skip critic if max revisions reached
    if revision_count >= MAX_REVISION_LOOPS:
        log.info(f"Max revisions ({MAX_REVISION_LOOPS}) reached — auto-approving")
        return {"is_validated": True, "final_response": output}

    prompt = f"""## Agent Output to Review (Intent: {intent})
{output[:3000]}

## Original User Query
{state.get('user_query', '')}

Evaluate this response:"""

    try:
        response = call_llm(prompt, CRITIC_SYSTEM_PROMPT, use_router_model=True)
        import re
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            approved = parsed.get("approved", True)
            feedback = parsed.get("feedback", "")
            score = parsed.get("score", 0.8)
        else:
            approved, feedback, score = True, "", 0.8
    except Exception as e:
        log.warning(f"Critic parsing failed: {e} — auto-approving")
        approved, feedback, score = True, "", 0.7

    log.info(f"Critic verdict: {'APPROVED' if approved else 'REVISION NEEDED'} (score: {score})")

    if approved:
        return {"is_validated": True, "final_response": output}
    else:
        return {
            "is_validated": False,
            "critic_feedback": feedback,
            "revision_count": revision_count + 1,
        }


def _get_agent_output(state: MaintenanceState) -> str:
    """Get the relevant agent output based on intent."""
    intent = state.get("intent", "general")
    if intent == "diagnosis":
        return state.get("diagnosis", "")
    elif intent == "rca":
        return state.get("root_cause", "")
    elif intent == "planning":
        return state.get("maintenance_plan", "")
    elif intent == "prediction":
        return state.get("final_response", "")
    return state.get("final_response", "")
