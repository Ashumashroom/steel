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
from ui.components import inject_components_css, hero_banner


# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Maintenance Wizard | Steel Plant AI",
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)

# Inject premium CSS
inject_css()
inject_components_css()

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"# {PAGE_ICON} Maintenance Wizard")
    st.caption(APP_SUBTITLE)
    st.divider()

    st.markdown("### ⚙️ Configuration")

    import config

    inference_options = ["gemini", "groq", "huggingface", "ollama"]

    # Use session_state as the source of truth so the selection survives
    # Streamlit reruns even if the config module gets re-imported/reset.
    if "inference_mode" not in st.session_state:
        st.session_state.inference_mode = (
            config.INFERENCE_MODE if config.INFERENCE_MODE in inference_options else "groq"
        )

    default_index = inference_options.index(st.session_state.inference_mode)

    inference_mode = st.selectbox(
        "Inference Backend",
        inference_options,
        index=default_index,
        help="Select the LLM inference backend to use",
        key="inference_mode_select",
    )

    # Persist selection across reruns
    st.session_state.inference_mode = inference_mode
    config.INFERENCE_MODE = inference_mode

    if inference_mode == "gemini":
        if "gemini_default_key" not in st.session_state:
            st.session_state.gemini_default_key = config.GEMINI_API_KEY

        api_key_input = st.text_input(
            "Gemini API Key (optional)",
            type="password",
            value="",
            help="Leave blank to use the host's configured key, or enter "
                 "your own Gemini key from https://aistudio.google.com/apikey",
            key="gemini_api_key_input",
            placeholder="Using host-configured key" if st.session_state.gemini_default_key else "Enter your Gemini API key",
        )

        if api_key_input:
            config.GEMINI_API_KEY = api_key_input
        else:
            config.GEMINI_API_KEY = st.session_state.gemini_default_key

    elif inference_mode == "groq":
        # Remember the original default key from .env so we can restore it
        # if the user clears the field after typing their own.
        if "groq_default_key" not in st.session_state:
            st.session_state.groq_default_key = config.GROQ_API_KEY

        api_key_input = st.text_input(
            "Groq API Key (optional)",
            type="password",
            value="",
            help="Leave blank to use the host's configured key, or enter "
                 "your own Groq key from https://console.groq.com/keys",
            key="groq_api_key_input",
            placeholder="Using host-configured key" if st.session_state.groq_default_key else "Enter your Groq API key",
        )

        if api_key_input:
            # User typed their own key — use it for this session
            config.GROQ_API_KEY = api_key_input
        else:
            # Field empty — fall back to the host's default key
            config.GROQ_API_KEY = st.session_state.groq_default_key

    elif inference_mode == "huggingface":
        if "hf_default_token" not in st.session_state:
            st.session_state.hf_default_token = config.HF_API_TOKEN

        api_key_input = st.text_input(
            "HuggingFace API Token (optional)",
            type="password",
            value="",
            placeholder="Using host-configured key" if st.session_state.hf_default_token else "Enter your HF token",
            key="hf_api_token_input",
        )

        if api_key_input:
            config.HF_API_TOKEN = api_key_input
        else:
            config.HF_API_TOKEN = st.session_state.hf_default_token

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
    st.caption("Built with LangGraph + Groq + ChromaDB")
    st.caption("TATA AI Hackathon 2026 — Round 2")


# ─── Main Content ─────────────────────────────────────────
hero_banner(
    title=APP_TITLE.replace("🏭", "").strip(),
    subtitle=APP_SUBTITLE,
    badges=["LangGraph", "Groq", "ChromaDB", "Agentic AI"],
)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 Maintenance Chat",
    "📊 Equipment Dashboard",
    "🚨 Alert Center",
    "📋 Reports",
    "📥 Log Upload",
    "🏭 Equipment Manager",
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

with tab5:
    from ui.log_upload import render_log_upload
    render_log_upload()

with tab6:
    from ui.equipment_manager_ui import render_equipment_manager
    render_equipment_manager()