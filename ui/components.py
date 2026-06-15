"""
Shared visual components — SteelGuard-style hero banners, KPI rows,
equipment cards, and status badges, built as HTML/CSS injected via
st.markdown(unsafe_allow_html=True).

IMPORTANT: All HTML strings are built as single-line strings (no leading
whitespace / indentation) because Streamlit's markdown renderer can
mis-interpret indented multi-line HTML as a code block, causing raw
HTML tags to render as visible text instead of being parsed.
"""
import streamlit as st

CRITICALITY_COLORS = {
    "critical": "#ef4444",
    "high": "#f59e0b",
    "medium": "#38bdf8",
    "low": "#22c55e",
}

RISK_COLORS = CRITICALITY_COLORS  # same palette for risk levels


def hero_banner(title: str, subtitle: str, badges: list[str] = None):
    """Render a SteelGuard-style gradient hero header."""
    badges = badges or []
    badge_html = "".join(f'<span class="hero-badge">{b}</span>' for b in badges)
    html = (
        '<div class="hero-banner"><div class="hero-glow"></div>'
        '<div class="hero-content">'
        f'<div class="hero-badges">{badge_html}</div>'
        f'<h1 class="hero-title">{title}</h1>'
        f'<p class="hero-subtitle">{subtitle}</p>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def kpi_row(items: list[dict]):
    """
    Render a row of KPI cards.
    Each item: {"label": str, "value": str, "delta": str (optional),
                 "color": "#hex" (optional), "icon": "emoji" (optional)}
    """
    cards_html = ""
    for item in items:
        color = item.get("color", "#38bdf8")
        icon = item.get("icon", "")
        delta = item.get("delta", "")
        delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
        cards_html += (
            f'<div class="kpi-card" style="--accent: {color};">'
            f'<div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{item["label"]}</div>'
            f'<div class="kpi-value">{item["value"]}</div>'
            f'{delta_html}'
            '</div>'
        )
    st.markdown(f'<div class="kpi-row">{cards_html}</div>', unsafe_allow_html=True)


def section_header(icon: str, title: str, subtitle: str = ""):
    """Render a styled section header with icon and optional subtitle."""
    sub_html = f'<p class="section-sub">{subtitle}</p>' if subtitle else ""
    html = (
        '<div class="section-header">'
        f'<span class="section-icon">{icon}</span>'
        f'<div><h3 class="section-title">{title}</h3>{sub_html}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def equipment_card_html(eid: str, name: str, etype: str, risk_level: str,
                          risk_score: float, rul_days, urgency: str) -> str:
    """Build the HTML for a single equipment status card (single-line)."""
    risk_level = (risk_level or "low").lower()
    if risk_level not in RISK_COLORS:
        risk_level = "low"
    color = RISK_COLORS.get(risk_level, "#38bdf8")
    pulse_class = " pulse" if risk_level == "critical" else ""
    rul_display = f"{rul_days} days" if rul_days is not None else "N/A"

    return (
        f'<div class="equip-card{pulse_class}" style="--accent: {color};">'
        '<div class="equip-card-top">'
        f'<span class="equip-id">{eid}</span>'
        f'<span class="badge badge-{risk_level}">{risk_level.upper()}</span>'
        '</div>'
        f'<div class="equip-name">{name}</div>'
        f'<div class="equip-type">{etype}</div>'
        '<div class="equip-stats">'
        f'<div><span class="stat-label">Risk Score</span><span class="stat-value">{risk_score:.2f}</span></div>'
        f'<div><span class="stat-label">RUL</span><span class="stat-value">{rul_display}</span></div>'
        '</div>'
        f'<div class="equip-urgency">{urgency}</div>'
        '</div>'
    )


def equipment_card_grid(cards: list[str], columns: int = 3):
    """Render a grid of equipment cards (HTML strings from equipment_card_html)."""
    grid_html = f'<div class="equip-grid" style="--cols: {columns};">' + "".join(cards) + "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)


def status_badge(level: str) -> str:
    """Return an HTML badge span for a risk/severity level
    (critical/high/medium/low). Use with st.markdown(..., unsafe_allow_html=True)."""
    level = (level or "low").lower()
    if level not in ("critical", "high", "medium", "low"):
        level = "low"
    return f'<span class="badge badge-{level}">{level.upper()}</span>'


# ──────────────────────────────────────────────
# CSS additions specific to these components
# ──────────────────────────────────────────────
COMPONENTS_CSS = """
<style>
/* ─── Hero Banner ────────────────────────────────────────── */
.hero-banner {
    position: relative;
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 24px;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(14,165,233,0.12), rgba(168,85,247,0.10), rgba(245,158,11,0.06));
    border: 1px solid rgba(56,189,248,0.18);
}

.hero-glow {
    position: absolute;
    top: -60%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(168,85,247,0.25), transparent 70%);
    pointer-events: none;
}

.hero-content { position: relative; z-index: 1; }

.hero-badges { margin-bottom: 10px; }

.hero-badge {
    display: inline-block;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.35);
    color: #7dd3fc;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-right: 8px;
}

.hero-title {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    margin: 4px 0 8px 0 !important;
    background: linear-gradient(135deg, #ffffff, #38bdf8, #a855f7) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
}

/* ─── KPI Row ────────────────────────────────────────────── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}

.kpi-card {
    background: rgba(13,19,33,0.75);
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 3px solid var(--accent, #38bdf8);
    border-radius: 14px;
    padding: 16px 18px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(56,189,248,0.12);
}

.kpi-icon { font-size: 1.4rem; margin-bottom: 6px; }

.kpi-label {
    color: #7c8aa0;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--accent, #38bdf8);
}

.kpi-delta {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 4px;
}

/* ─── Section Header ─────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 14px 0;
}

.section-icon {
    font-size: 1.6rem;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 10px;
    padding: 6px 10px;
}

.section-title {
    margin: 0 !important;
    color: #e2e8f0 !important;
    font-size: 1.15rem !important;
}

.section-sub {
    margin: 2px 0 0 0;
    color: #64748b;
    font-size: 0.85rem;
}

/* ─── Equipment Card Grid ────────────────────────────────── */
.equip-grid {
    display: grid;
    grid-template-columns: repeat(var(--cols, 3), 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

@media (max-width: 900px) {
    .equip-grid { grid-template-columns: 1fr; }
}

.equip-card {
    background: rgba(13,19,33,0.75);
    border: 1px solid rgba(255,255,255,0.07);
    border-top: 3px solid var(--accent, #38bdf8);
    border-radius: 14px;
    padding: 16px 18px;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.equip-card:hover {
    transform: translateY(-3px);
    border-color: var(--accent, #38bdf8);
}

.equip-card.pulse {
    animation: card-pulse 2.2s infinite;
}

@keyframes card-pulse {
    0%, 100% { box-shadow: 0 0 0px rgba(239,68,68,0.0); }
    50% { box-shadow: 0 0 24px rgba(239,68,68,0.45); }
}

.equip-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.equip-id {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: #e2e8f0;
    font-size: 0.95rem;
}

.equip-name {
    color: #cbd5e1;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 2px;
}

.equip-type {
    color: #64748b;
    font-size: 0.78rem;
    margin-bottom: 12px;
}

.equip-stats {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.equip-stats > div {
    display: flex;
    flex-direction: column;
}

.stat-label {
    color: #64748b;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-family: 'JetBrains Mono', monospace;
    color: #e2e8f0;
    font-weight: 700;
    font-size: 1rem;
}

.equip-urgency {
    color: #94a3b8;
    font-size: 0.78rem;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 8px;
}

/* ─── Badges (shared with status_badge) ──────────────────── */
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
</style>
"""


def inject_components_css():
    """Inject the additional component CSS. Call once per page alongside inject_css()."""
    st.markdown(COMPONENTS_CSS, unsafe_allow_html=True)