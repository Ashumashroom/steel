"""
Equipment Health Dashboard — KPI overview, equipment card grid,
and interactive Plotly charts per asset.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SENSOR_DIR, SENSOR_PARAMS, get_equipment
from ui.components import (
    inject_components_css, kpi_row, section_header,
    equipment_card_html, equipment_card_grid,
)


def render_dashboard():
    """Render the equipment health dashboard tab."""
    inject_components_css()

    equipment_registry = get_equipment()

    # Load risk data for the whole fleet
    try:
        from analytics.risk_classifier import get_all_risk_levels
        all_risks = get_all_risk_levels()
        risk_map = {r["equipment_id"]: r for r in all_risks}
    except Exception:
        all_risks = []
        risk_map = {}

    # ─── Fleet KPI Row ───────────────────────────────────────
    total_units = len(equipment_registry)
    critical_count = sum(1 for r in all_risks if r["risk_level"] == "critical")
    high_count = sum(1 for r in all_risks if r["risk_level"] == "high")
    avg_score = (sum(r["risk_score"] for r in all_risks) / len(all_risks)) if all_risks else 0
    rul_values = [r.get("rul_days") for r in all_risks if r.get("rul_days") is not None]
    min_rul = min(rul_values) if rul_values else None

    section_header("📊", "Fleet Overview", "Real-time health summary across all monitored equipment")

    kpi_row([
        {"label": "Total Equipment", "value": str(total_units), "icon": "🏭", "color": "#38bdf8"},
        {"label": "Critical Alerts", "value": str(critical_count), "icon": "🔴", "color": "#ef4444"},
        {"label": "High Risk", "value": str(high_count), "icon": "🟠", "color": "#f59e0b"},
        {"label": "Avg Risk Score", "value": f"{avg_score:.2f}", "icon": "📈", "color": "#a855f7"},
        {"label": "Lowest RUL", "value": f"{min_rul:.0f} days" if min_rul is not None else "N/A",
         "icon": "⏳", "color": "#22c55e"},
    ])

    # ─── Equipment Card Grid ─────────────────────────────────
    section_header("🏗️", "Equipment Fleet", "Click an equipment below in the selector to view detailed sensor trends")

    cards = []
    for eid, info in equipment_registry.items():
        r = risk_map.get(eid, {})
        cards.append(equipment_card_html(
            eid=eid,
            name=info["name"],
            etype=info["type"],
            risk_level=r.get("risk_level", "low"),
            risk_score=r.get("risk_score", 0.0),
            rul_days=r.get("rul_days"),
            urgency=r.get("urgency", "No data"),
        ))
    equipment_card_grid(cards, columns=3)

    st.divider()

    # ─── Equipment Selector + Detail View ───────────────────
    section_header("🔍", "Equipment Detail", "Sensor trends and anomaly analysis for the selected unit")

    equipment_options = {f"{eid} — {info['name']}": eid for eid, info in equipment_registry.items()}
    selected = st.selectbox("Select Equipment", list(equipment_options.keys()))
    eid = equipment_options[selected]
    info = equipment_registry[eid]
    risk = risk_map.get(eid, {})

    kpi_row([
        {"label": "Risk Level", "value": risk.get("risk_level", "N/A").upper(),
         "icon": "⚠️", "color": _risk_color(risk.get("risk_level"))},
        {"label": "Risk Score", "value": f"{risk.get('risk_score', 0):.2f}", "icon": "📊", "color": "#38bdf8"},
        {"label": "RUL", "value": f"{risk.get('rul_days', 'N/A')} days", "icon": "⏳", "color": "#a855f7"},
        {"label": "Criticality", "value": info.get("criticality", "N/A").upper(), "icon": "🏷️", "color": "#f59e0b"},
    ])

    # ─── Sensor Charts ─────────────────────────────────────
    csv_path = SENSOR_DIR / f"{eid}_sensors.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        etype = info["type"]
        params = [c for c in SENSOR_PARAMS.get(etype, []) if c in df.columns]

        # Run anomaly detection
        try:
            from analytics.anomaly_detector import get_detector
            detector = get_detector()
            df = detector.detect(eid, df)
            has_anomaly = True
        except Exception:
            has_anomaly = False

        # Sensor trend charts
        section_header("📈", "Sensor Trends", f"{len(params)} monitored signals for {info['type']}")
        cols_per_row = 2
        for i in range(0, len(params), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(params):
                    param = params[i + j]
                    with col:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df["timestamp"], y=df[param],
                            mode="lines", name=param,
                            line=dict(color="#38bdf8", width=1.5),
                        ))
                        # Highlight anomalies
                        if has_anomaly and "is_anomaly" in df.columns:
                            anomaly_df = df[df["is_anomaly"]]
                            if len(anomaly_df) > 0:
                                fig.add_trace(go.Scatter(
                                    x=anomaly_df["timestamp"], y=anomaly_df[param],
                                    mode="markers", name="Anomaly",
                                    marker=dict(color="#ef4444", size=5, symbol="x"),
                                ))
                        fig.update_layout(
                            title=param.replace("_", " ").title(),
                            template="plotly_dark",
                            height=280,
                            margin=dict(l=40, r=20, t=40, b=30),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(17,24,39,0.5)",
                            showlegend=False,
                            font=dict(family="Inter, sans-serif", color="#94a3b8"),
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # Anomaly score timeline
        if has_anomaly and "anomaly_score" in df.columns:
            section_header("🚨", "Anomaly Score Timeline", "Higher values indicate more abnormal sensor behavior")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["timestamp"], y=df["anomaly_score"],
                fill="tozeroy", name="Anomaly Score",
                line=dict(color="#f59e0b", width=1),
                fillcolor="rgba(245,158,11,0.15)",
            ))
            fig.add_hline(y=df["anomaly_score"].quantile(0.95),
                          line_dash="dash", line_color="#ef4444",
                          annotation_text="95th Percentile Threshold")
            fig.update_layout(
                template="plotly_dark", height=300,
                margin=dict(l=40, r=20, t=30, b=30),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,24,39,0.5)",
                font=dict(family="Inter, sans-serif", color="#94a3b8"),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No sensor data found for {eid}")

    # ─── Fleet Table (detailed) ─────────────────────────────
    st.divider()
    section_header("📋", "Fleet Health Table", "Sorted by risk score, highest first")
    if risk_map:
        fleet_data = []
        for r in sorted(risk_map.values(), key=lambda x: x["risk_score"], reverse=True):
            fleet_data.append({
                "Equipment": f"{r['equipment_id']} — {r['equipment_name']}",
                "Risk": r["risk_level"].upper(),
                "Score": f"{r['risk_score']:.2f}",
                "RUL (days)": r.get("rul_days", "N/A"),
                "Urgency": r["urgency"],
            })
        st.dataframe(pd.DataFrame(fleet_data), use_container_width=True, hide_index=True)


def _risk_color(level: str) -> str:
    colors = {"critical": "#ef4444", "high": "#f59e0b", "medium": "#38bdf8", "low": "#22c55e"}
    return colors.get((level or "low").lower(), "#38bdf8")