"""
Diagnostic Agent — fault diagnosis with RAG-retrieved evidence.
"""
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.llm_helper import call_llm
from rag.retriever import retrieve, format_context, get_source_citations
from utils.logger import get_logger

log = get_logger("agents.diagnostic")

DIAG_SYSTEM_PROMPT = """You are an expert maintenance diagnostic agent for a steel manufacturing plant.
Using the provided context from equipment manuals, maintenance logs, and SOPs, diagnose the equipment issue described by the user.

Your diagnosis MUST include:
1. **Probable Fault**: The most likely fault with confidence level (high/medium/low)
2. **Evidence**: Specific references from the retrieved documents supporting your diagnosis
3. **Root Indicators**: Key symptoms/sensor readings that point to this fault
4. **Immediate Action**: What should be done RIGHT NOW
5. **Risk Level**: low / medium / high / critical

Format your response clearly with markdown headers. Be specific and actionable.
If you're unsure, state your confidence level honestly. NEVER fabricate maintenance procedures."""


def diagnostic_node(state: MaintenanceState) -> dict:
    """LangGraph node: diagnose equipment fault."""
    query = state["user_query"]
    equipment_id = state.get("equipment_id")
    critic_feedback = state.get("critic_feedback")

    log.info(f"Diagnosing: {query[:60]}...")

    # Retrieve relevant documents
    filter_meta = None
    if equipment_id:
        filter_meta = {"equipment_id": equipment_id}

    docs = retrieve(query, filter_metadata=filter_meta)
    context = format_context(docs)
    sources = get_source_citations(docs)

    # Build prompt
    prompt = f"""## Equipment Query
{query}

## Equipment ID: {equipment_id or 'Not specified'}

## Retrieved Knowledge Base Context
{context}
"""
    if critic_feedback:
        prompt += f"\n## Previous Attempt Feedback (please address these issues)\n{critic_feedback}\n"

    prompt += "\nProvide a comprehensive diagnosis:"

    response = call_llm(prompt, DIAG_SYSTEM_PROMPT)

    return {
        "diagnosis": response,
        "retrieved_context": context,
        "retrieved_sources": sources,
    }
