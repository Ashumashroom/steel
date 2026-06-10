"""
Maintenance Planner Agent — prioritized recommendations with spare parts awareness.
"""
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from rag.retriever import retrieve, format_context, get_source_citations
from utils.logger import get_logger

log = get_logger("agents.planner")

PLANNER_SYSTEM_PROMPT = """You are a maintenance planning specialist for a steel manufacturing plant.
Generate a comprehensive, prioritized maintenance plan based on the query and retrieved context.

Your plan MUST include:
1. **Immediate Actions** (next 4 hours): Critical safety or operational steps
2. **Short-Term Plan** (next 7 days): Scheduled repairs and inspections
3. **Long-Term Strategy** (next 30 days): Preventive measures and monitoring
4. **Spare Parts Required**: List specific parts with quantities and procurement notes
5. **Resource Requirements**: Personnel, tools, estimated downtime
6. **Priority Ranking**: Justify the ordering based on:
   - Process criticality
   - Delay severity
   - Spares availability
   - Procurement lead time

Use specific details from the maintenance documentation. Be actionable and precise."""


def maintenance_planner_node(state: MaintenanceState) -> dict:
    """LangGraph node: generate maintenance plan."""
    query = state["user_query"]
    equipment_id = state.get("equipment_id")
    critic_feedback = state.get("critic_feedback")

    log.info(f"Planning: {query[:60]}...")

    # Retrieve SOPs, spare parts info, and maintenance history
    docs = retrieve(query)
    context = format_context(docs)
    sources = get_source_citations(docs)

    prompt = f"""## Maintenance Planning Request
{query}

## Equipment ID: {equipment_id or 'All equipment'}

## Relevant Documentation & Spare Parts Info
{context}
"""
    if critic_feedback:
        prompt += f"\n## Revision Feedback\n{critic_feedback}\n"

    prompt += "\nGenerate a detailed maintenance plan:"

    response = call_llm(prompt, PLANNER_SYSTEM_PROMPT)

    return {
        "maintenance_plan": response,
        "retrieved_context": context,
        "retrieved_sources": sources,
    }
