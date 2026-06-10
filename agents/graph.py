"""
Main LangGraph Workflow — orchestrates the multi-agent maintenance wizard.

Flow: User Query → Router → Specialist Agent → Critic → (Revise | Approve) → Response
"""
from pathlib import Path
from langgraph.graph import StateGraph, END

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.state import MaintenanceState
from agents.router_agent import router_node
from agents.diagnostic_agent import diagnostic_node
from agents.rca_agent import rca_node
from agents.predictive_agent import predictive_node
from agents.maintenance_planner import maintenance_planner_node
from agents.critic_agent import critic_node
from agents.llm_helper import call_llm
from rag.retriever import retrieve, format_context, get_source_citations
from utils.logger import get_logger

log = get_logger("agents.graph")


# ─── General Q&A Node ─────────────────────────────────────────
def general_node(state: MaintenanceState) -> dict:
    """Handle general questions about equipment, processes, or procedures."""
    query = state["user_query"]
    docs = retrieve(query)
    context = format_context(docs)
    sources = get_source_citations(docs)

    prompt = f"""## User Question
{query}

## Relevant Documentation
{context}

Answer the question based on the provided documentation. Be helpful and specific."""

    system = (
        "You are a knowledgeable assistant for a steel manufacturing plant. "
        "Answer questions about equipment, processes, and maintenance procedures "
        "using the provided documentation. Cite your sources."
    )
    response = call_llm(prompt, system)
    return {
        "final_response": response,
        "retrieved_context": context,
        "retrieved_sources": sources,
    }


# ─── Format Response Node ─────────────────────────────────────
def format_response_node(state: MaintenanceState) -> dict:
    """Format the final response with sources and alerts."""
    response = state.get("final_response", "")
    sources = state.get("retrieved_sources", [])
    alerts = state.get("alerts", [])

    # Append source citations if available
    if sources:
        response += "\n\n---\n**Sources:**\n"
        for s in sources[:5]:
            response += f"- {s}\n"

    # Append alerts if any
    if alerts:
        response += "\n**Active Alerts:**\n"
        for a in alerts:
            severity = a.get("severity", "info").upper()
            response += f"- [{severity}] {a.get('message', '')}\n"

    return {"final_response": response}


# ─── Routing Logic ─────────────────────────────────────────────
def route_to_agent(state: MaintenanceState) -> str:
    """Conditional edge: route to specialist agent based on intent."""
    intent = state.get("intent", "general")
    routes = {
        "diagnosis": "diagnostic",
        "rca": "rca",
        "prediction": "predictive",
        "planning": "planner",
    }
    return routes.get(intent, "general")


def should_revise(state: MaintenanceState) -> str:
    """Conditional edge: check if critic approved or needs revision."""
    if state.get("is_validated", False):
        return "format"
    # Route back to the original agent for revision
    intent = state.get("intent", "general")
    routes = {
        "diagnosis": "diagnostic",
        "rca": "rca",
        "planning": "planner",
    }
    return routes.get(intent, "format")


# ─── Build Graph ───────────────────────────────────────────────
def build_graph() -> StateGraph:
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(MaintenanceState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("rca", rca_node)
    graph.add_node("predictive", predictive_node)
    graph.add_node("planner", maintenance_planner_node)
    graph.add_node("general", general_node)
    graph.add_node("critic", critic_node)
    graph.add_node("format", format_response_node)

    # Set entry point
    graph.set_entry_point("router")

    # Router → Specialist Agent
    graph.add_conditional_edges("router", route_to_agent, {
        "diagnostic": "diagnostic",
        "rca": "rca",
        "predictive": "predictive",
        "planner": "planner",
        "general": "general",
    })

    # Specialist Agents → Critic (except predictive which goes directly)
    graph.add_edge("diagnostic", "critic")
    graph.add_edge("rca", "critic")
    graph.add_edge("planner", "critic")
    graph.add_edge("predictive", "format")  # predictive skips critic
    graph.add_edge("general", "format")     # general skips critic

    # Critic → Revise or Format
    graph.add_conditional_edges("critic", should_revise, {
        "diagnostic": "diagnostic",
        "rca": "rca",
        "planner": "planner",
        "format": "format",
    })

    # Format → END
    graph.add_edge("format", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None

def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
        log.info("LangGraph workflow compiled successfully")
    return _compiled_graph


def run_query(query: str, conversation_history: list = None) -> dict:
    """Run a user query through the full agent pipeline."""
    graph = get_graph()
    initial_state = {
        "user_query": query,
        "conversation_history": conversation_history or [],
        "intent": "",
        "equipment_id": None,
        "retrieved_context": "",
        "retrieved_sources": [],
        "diagnosis": None,
        "root_cause": None,
        "predictions": None,
        "maintenance_plan": None,
        "risk_assessment": None,
        "is_validated": False,
        "critic_feedback": None,
        "revision_count": 0,
        "final_response": "",
        "alerts": [],
    }

    result = graph.invoke(initial_state)
    return result
