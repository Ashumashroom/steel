"""
🏭 Intelligent Maintenance Wizard — Main Streamlit Application
Steel Manufacturing | Agentic AI-Powered Decision Support

TATA AI Hackathon — Round 2
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_TITLE, APP_SUBTITLE, PAGE_ICON, LAYOUT
from ui.styles import inject_css


# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Maintenance Wizard | Steel Plant AI",
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)

# Inject premium CSS
inject_css()

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"# {PAGE_ICON} Maintenance Wizard")
    st.caption(APP_SUBTITLE)
    st.divider()

    st.markdown("### ⚙️ Configuration")
    inference_mode = st.selectbox(
        "Inference Backend",
        ["huggingface", "groq", "ollama"],
        index=0,
        help="Select the LLM inference backend to use",
    )

    # Update config at runtime
    import config
    config.INFERENCE_MODE = inference_mode

    if inference_mode == "groq":
        api_key = st.text_input("Groq API Key", type="password")
        if api_key:
            config.GROQ_API_KEY = api_key
    elif inference_mode == "huggingface":
        api_key = st.text_input("HuggingFace API Token", type="password")
        if api_key:
            config.HF_API_TOKEN = api_key

    st.divider()

    # Data initialization
    st.markdown("### 📁 Data Management")
    if st.button("🔄 Generate Synthetic Data", use_container_width=True):
        with st.spinner("Generating data..."):
            from utils.data_generator import generate_all
            generate_all()
        st.success("Data generated!")

    if st.button("📚 Index Documents (RAG)", use_container_width=True):
        with st.spinner("Indexing documents into ChromaDB..."):
            from rag.document_loader import load_all_documents, chunk_documents
            from rag.vector_store import index_documents
            docs = load_all_documents()
            chunks = chunk_documents(docs)
            index_documents(chunks)
        st.success(f"Indexed {len(chunks)} chunks!")

    st.divider()

    # Feedback stats
    try:
        from utils.feedback import get_feedback_stats
        stats = get_feedback_stats()
        if stats["total"] > 0:
            st.markdown("### 📊 Feedback Stats")
            st.metric("Satisfaction", f"{stats['satisfaction_rate']}%")
            st.caption(f"{stats['positive']} positive / {stats['negative']} negative")
    except Exception:
        pass

    st.divider()
    st.caption("Built with LangGraph + HuggingFace + ChromaDB")
    st.caption("TATA AI Hackathon 2026 — Round 2")


# ─── Main Content ─────────────────────────────────────────
st.markdown(f"# {APP_TITLE}")
st.caption(APP_SUBTITLE)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Maintenance Chat",
    "📊 Equipment Dashboard",
    "🚨 Alert Center",
    "📋 Reports",
])

with tab1:
    from ui.chat_interface import render_chat_interface
    render_chat_interface()

with tab2:
    from ui.dashboard import render_dashboard
    render_dashboard()

with tab3:
    from ui.alert_panel import render_alert_panel
    render_alert_panel()

with tab4:
    from ui.report_generator import render_report_generator
    render_report_generator()
