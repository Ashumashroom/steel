"""
Premium dark-mode CSS for the Maintenance Wizard Streamlit UI.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── Global ─────────────────────────────────────────────── */
.stApp {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0e17 0%, #0d1321 50%, #0a1628 100%);
}

/* ─── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #111827 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.1);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #38bdf8 !important;
}

/* ─── Glass Cards ────────────────────────────────────────── */
.glass-card {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.glass-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 8px 40px rgba(56, 189, 248, 0.1);
    transform: translateY(-2px);
}

/* ─── Status Cards ───────────────────────────────────────── */
.status-critical {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

.status-high {
    background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.05));
    border-left: 4px solid #f59e0b;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

.status-medium {
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(59,130,246,0.05));
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

.status-low {
    background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05));
    border-left: 4px solid #22c55e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* ─── Metric Cards ───────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.6);
    border: 1px solid rgba(56, 189, 248, 0.1);
    border-radius: 12px;
    padding: 16px !important;
}

div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
    font-weight: 600 !important;
}

/* ─── Chat Messages ──────────────────────────────────────── */
.stChatMessage[data-testid="stChatMessage"] {
    background: rgba(17, 24, 39, 0.5) !important;
    border: 1px solid rgba(56, 189, 248, 0.1) !important;
    border-radius: 12px !important;
    margin: 8px 0 !important;
}

/* ─── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 24px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0284c7, #0891b2) !important;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* ─── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(17, 24, 39, 0.5);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 20px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
    color: white !important;
}

/* ─── Tables ─────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid rgba(56, 189, 248, 0.1) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ─── Headers ────────────────────────────────────────────── */
h1 {
    background: linear-gradient(135deg, #38bdf8, #06b6d4, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

h2, h3 {
    color: #e2e8f0 !important;
}

/* ─── Dividers ───────────────────────────────────────────── */
hr {
    border-color: rgba(56, 189, 248, 0.15) !important;
}

/* ─── Alert Badges ───────────────────────────────────────── */
.alert-badge-critical {
    display: inline-block;
    background: #ef4444;
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    animation: pulse 2s infinite;
}

.alert-badge-high {
    display: inline-block;
    background: #f59e0b;
    color: #111;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ─── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1321; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
