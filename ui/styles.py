"""
Premium dark-mode CSS for the Maintenance Wizard Streamlit UI.
SteelGuard-inspired "command-center" theme: near-black background,
glowing multi-color accents, badge-style status pills.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ─── Global ─────────────────────────────────────────────── */
.stApp {
    font-family: 'Inter', sans-serif;
    background:
        radial-gradient(circle at 15% 0%, rgba(56,189,248,0.06) 0%, transparent 40%),
        radial-gradient(circle at 85% 100%, rgba(168,85,247,0.06) 0%, transparent 40%),
        linear-gradient(135deg, #060a12 0%, #0a0f1c 50%, #060c16 100%);
}

/* ─── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b14 0%, #0c1320 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.12);
}

section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    background: linear-gradient(135deg, #38bdf8, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

/* ─── Glass Cards ────────────────────────────────────────── */
.glass-card {
    background: rgba(13, 19, 33, 0.75);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    transition: all 0.25s ease;
}

.glass-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 0 0 1px rgba(56,189,248,0.25), 0 12px 40px rgba(56, 189, 248, 0.12);
    transform: translateY(-2px);
}

/* ─── Status Cards (alert rows) ──────────────────────────── */
.status-critical {
    background: linear-gradient(135deg, rgba(239,68,68,0.16), rgba(239,68,68,0.04));
    border: 1px solid rgba(239,68,68,0.35);
    border-left: 4px solid #ef4444;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 0 24px rgba(239,68,68,0.08);
}

.status-high {
    background: linear-gradient(135deg, rgba(245,158,11,0.16), rgba(245,158,11,0.04));
    border: 1px solid rgba(245,158,11,0.3);
    border-left: 4px solid #f59e0b;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

.status-medium {
    background: linear-gradient(135deg, rgba(56,189,248,0.14), rgba(56,189,248,0.04));
    border: 1px solid rgba(56,189,248,0.3);
    border-left: 4px solid #38bdf8;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

.status-low {
    background: linear-gradient(135deg, rgba(34,197,94,0.14), rgba(34,197,94,0.04));
    border: 1px solid rgba(34,197,94,0.3);
    border-left: 4px solid #22c55e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* ─── Metric Cards ───────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(13, 19, 33, 0.7);
    border: 1px solid rgba(56, 189, 248, 0.14);
    border-radius: 12px;
    padding: 16px !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 0 20px rgba(56,189,248,0.1);
}

div[data-testid="stMetric"] label {
    color: #7c8aa0 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    background: linear-gradient(135deg, #38bdf8, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}

/* ─── Chat Messages ──────────────────────────────────────── */
.stChatMessage[data-testid="stChatMessage"] {
    background: rgba(13, 19, 33, 0.6) !important;
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 12px !important;
    margin: 8px 0 !important;
}

/* ─── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 8px 24px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 4px 24px rgba(168, 85, 247, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Primary (form-submit) buttons get extra glow */
.stButton > button[kind="primary"],
button[kind="formSubmit"] {
    background: linear-gradient(135deg, #06b6d4, #a855f7, #f59e0b) !important;
    box-shadow: 0 0 20px rgba(56,189,248,0.25) !important;
}

/* ─── Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(13, 19, 33, 0.6);
    border: 1px solid rgba(56,189,248,0.08);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 20px !important;
    color: #7c8aa0 !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #a855f7) !important;
    color: white !important;
    box-shadow: 0 2px 16px rgba(56,189,248,0.25) !important;
}

/* ─── Tables ─────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid rgba(56, 189, 248, 0.12) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ─── Headers ────────────────────────────────────────────── */
h1 {
    background: linear-gradient(135deg, #38bdf8, #a855f7, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.01em;
}

h2, h3 {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

h4, h5 {
    color: #c5d0e0 !important;
}

/* ─── Captions / muted text ──────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #64748b !important;
}

/* ─── Dividers ───────────────────────────────────────────── */
hr {
    border-color: rgba(56, 189, 248, 0.12) !important;
}

/* ─── Status / Severity Badges ──────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.badge-critical {
    background: rgba(239,68,68,0.18);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.4);
    animation: pulse-glow 2s infinite;
}

.badge-high {
    background: rgba(245,158,11,0.18);
    color: #fcd34d;
    border: 1px solid rgba(245,158,11,0.4);
}

.badge-medium {
    background: rgba(56,189,248,0.16);
    color: #7dd3fc;
    border: 1px solid rgba(56,189,248,0.4);
}

.badge-low {
    background: rgba(34,197,94,0.16);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.4);
}

/* Legacy aliases kept for backward-compatibility */
.alert-badge-critical {
    display: inline-block;
    background: #ef4444;
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    animation: pulse-glow 2s infinite;
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

@keyframes pulse-glow {
    0%, 100% { opacity: 1; box-shadow: 0 0 0px rgba(239,68,68,0.5); }
    50% { opacity: 0.75; box-shadow: 0 0 12px rgba(239,68,68,0.5); }
}

/* ─── Toggle (Fast mode etc.) ─────────────────────────────── */
[data-testid="stToggle"] label {
    color: #c5d0e0 !important;
}

/* ─── Scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #070b14; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #38bdf8, #a855f7); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }
.chat-attachment {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #7dd3fc;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.78rem;
    margin-bottom: 6px;
    
}
    .feedback-ack {
    display: inline-block;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.3);
    color: #86efac;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 0.9rem;
}
.feedback-prompt {
    display: inline-block;
    background: rgba(168,85,247,0.08);
    border: 1px solid rgba(168,85,247,0.25);
    color: #c4b5fd;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 0.82rem;
    margin-top: 6px;
}
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def status_badge(level: str) -> str:
    """Return an HTML badge span for a risk/severity level
    (critical/high/medium/low). Use with st.markdown(..., unsafe_allow_html=True)."""
    level = (level or "low").lower()
    if level not in ("critical", "high", "medium", "low"):
        level = "low"
    return f'<span class="badge badge-{level}">{level.upper()}</span>'