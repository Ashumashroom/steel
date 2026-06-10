"""
Root Cause Analysis Agent — correlates history, sensor trends, and failure modes.
"""
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from rag.retriever import retrieve, format_context, get_source_citations
from utils.logger import get_logger

log = get_logger("agents.rca")

RCA_SYSTEM_PROMPT = """You are a Root Cause Analysis (RCA) specialist for steel manufacturing equipment.
Analyze the failure/incident described by the user using the provided historical data and documentation.

Your RCA report MUST include:
1. **Incident Summary**: Brief description of what happened
2. **5-Why Analysis**: Systematically drill down to the root cause
   - Why 1: [immediate cause]
   - Why 2: [underlying cause]
   - Why 3: [systemic cause]
   - Why 4: [process cause]
   - Why 5: [root cause]
3. **Contributing Factors**: Environmental, operational, and maintenance-related factors
4. **Evidence**: References to historical patterns from logs and manuals
5. **Corrective Actions**: Immediate, short-term (7 days), and long-term (30 days)
6. **Preventive Measures**: How to prevent recurrence

Be systematic, thorough, and reference specific evidence. Use markdown formatting."""


def rca_node(state: MaintenanceState) -> dict:
    """LangGraph node: perform root cause analysis."""
    query = state["user_query"]
    equipment_id = state.get("equipment_id")
    critic_feedback = state.get("critic_feedback")

    log.info(f"RCA: {query[:60]}...")

    docs = retrieve(query)
    context = format_context(docs)
    sources = get_source_citations(docs)

    prompt = f"""## Incident / Failure to Analyze
{query}

## Equipment ID: {equipment_id or 'Not specified'}

## Historical Data & Documentation
{context}
"""
    if critic_feedback:
        prompt += f"\n## Revision Feedback\n{critic_feedback}\n"

    prompt += "\nProvide a comprehensive Root Cause Analysis:"

    response = call_llm(prompt, RCA_SYSTEM_PROMPT)

    return {
        "root_cause": response,
        "retrieved_context": context,
        "retrieved_sources": sources,
    }
