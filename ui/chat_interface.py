"""
Chat interface component for the Maintenance Wizard.
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def render_chat_interface():
    """Render the chat interface tab."""
    st.markdown("### 💬 Maintenance Assistant")
    st.caption("Ask about equipment diagnosis, root cause analysis, predictions, or maintenance planning.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": _welcome_message()}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a maintenance question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing with multi-agent system..."):
                response = _get_response(prompt)
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Feedback buttons
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button("👍", key=f"up_{len(st.session_state.messages)}"):
                _save_feedback(prompt, response, 1)
                st.toast("Thanks for the feedback!")
        with col2:
            if st.button("👎", key=f"down_{len(st.session_state.messages)}"):
                _save_feedback(prompt, response, -1)
                st.toast("We'll work on improving!")

    # Sidebar sample queries
    with st.sidebar:
        st.markdown("### 💡 Sample Queries")
        samples = [
            "Blast Furnace BF-001 showing unusual vibration readings. What could be wrong?",
            "Perform root cause analysis for bearing failure on RM-001",
            "What is the remaining useful life of Rolling Mill Motor RM-003?",
            "Generate a maintenance plan for BOF-001 for next quarter",
            "Show me the health status of all critical equipment",
        ]
        for s in samples:
            if st.button(s, key=f"sample_{hash(s)}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": s})
                st.rerun()


def _welcome_message() -> str:
    return """Welcome to the **Intelligent Maintenance Wizard** 🏭

I can help you with:
- 🔧 **Diagnosis** — Identify probable faults from symptoms or error codes
- 🔍 **Root Cause Analysis** — Drill down to the fundamental cause of failures
- 📊 **Predictions** — Check equipment health, anomalies, and remaining useful life
- 📋 **Maintenance Planning** — Get prioritized action plans with spare parts info
- ❓ **General Queries** — Ask about SOPs, equipment manuals, or procedures

**Try asking:** _"BF-001 is showing high vibration. What could be wrong?"_"""


def _get_response(query: str) -> str:
    """Get response from the LangGraph agent pipeline."""
    try:
        from agents.graph import run_query
        result = run_query(query)
        return result.get("final_response", "I couldn't generate a response. Please try again.")
    except Exception as e:
        return f"**Error:** {str(e)}\n\nPlease check your LLM configuration in `.env` file."


def _save_feedback(query: str, response: str, rating: int):
    try:
        from utils.feedback import save_feedback
        save_feedback(query, "", "", response, rating)
    except Exception:
        pass
