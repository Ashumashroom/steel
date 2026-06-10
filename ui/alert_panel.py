"""
Alert Panel — real-time abnormality alerts with severity badges.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EQUIPMENT


def render_alert_panel():
    """Render the alert center tab."""
    st.markdown("### 🚨 Alert Center")
    st.caption("Real-time abnormality alerts and equipment warnings")

    try:
        from analytics.risk_classifier import get_all_risk_levels
        all_risks = get_all_risk_levels()
    except Exception as e:
        st.error(f"Could not load risk data: {e}")
        return

    # Filter controls
    col1, col2 = st.columns([1, 3])
    with col1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            ["critical", "high", "medium", "low"],
            default=["critical", "high"],
        )

    # Active alerts
    alerts = [r for r in all_risks if r["risk_level"] in severity_filter]

    if not alerts:
        st.info("No alerts matching the selected severity filters.")
        return

    st.markdown(f"**{len(alerts)} active alerts**")

    for alert in alerts:
        level = alert["risk_level"]
        css_class = f"status-{level}"
        icon = {"critical": "🔴", "high": "🟠", "medium": "🔵", "low": "🟢"}.get(level, "⚪")

        st.markdown(f"""
        <div class="{css_class}">
            <strong>{icon} {alert['equipment_name']} ({alert['equipment_id']})</strong><br>
            <span style="color: #94a3b8;">Risk Level: <strong>{level.upper()}</strong> | 
            Score: {alert['risk_score']:.3f} | 
            RUL: {alert.get('rul_days', 'N/A')} days</span><br>
            <span style="color: #e2e8f0;">{alert['urgency']}</span>
        </div>
        """, unsafe_allow_html=True)

    # Alert summary chart
    st.divider()
    st.markdown("#### Alert Distribution")
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for r in all_risks:
        counts[r["risk_level"].capitalize()] += 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Critical", counts["Critical"])
    with col2:
        st.metric("🟠 High", counts["High"])
    with col3:
        st.metric("🔵 Medium", counts["Medium"])
    with col4:
        st.metric("🟢 Low", counts["Low"])
