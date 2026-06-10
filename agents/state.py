"""
Shared state schema for the LangGraph maintenance wizard.
"""
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class MaintenanceState(TypedDict):
    """State flowing through the LangGraph agent workflow."""
    # User input
    user_query: str
    conversation_history: Annotated[list, add_messages]

    # Routing
    intent: str  # "diagnosis", "rca", "prediction", "planning", "general"
    equipment_id: Optional[str]

    # Retrieved context
    retrieved_context: str
    retrieved_sources: list[str]

    # Agent outputs
    diagnosis: Optional[str]
    root_cause: Optional[str]
    predictions: Optional[dict]
    maintenance_plan: Optional[str]
    risk_assessment: Optional[dict]

    # Validation
    is_validated: bool
    critic_feedback: Optional[str]
    revision_count: int

    # Final output
    final_response: str
    alerts: list[dict]
