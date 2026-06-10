"""
Equipment Health Dashboard — interactive Plotly charts and status cards.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EQUIPMENT, SENSOR_DIR, SENSOR_PARAMS


def render_dashboard():
    """Render the equipment health dashboard tab."""
    st.markdown("### 📊 Equipment Health Dashboard")

    # Equipment selector
    equipment_options = {f"{eid} — {info['name']}": eid for eid, info in EQUIPMENT.items()}
    selected = st.selectbox("Select Equipment", list(equipment_options.keys()))
    eid = equipment_options[selected]
    info = EQUIPMENT[eid]

    # Load risk data
    try:
        from analytics.risk_classifier import get_all_risk_levels
        all_risks = get_all_risk_levels()
        risk_map = {r["equipment_id"]: r for r in all_risks}
    except Exception:
        risk_map = {}

    # ─── Status Cards ──────────────────────────────────────
    risk = risk_map.get(eid, {})
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        level = risk.get("risk_level", "N/A").upper()
        st.metric("Risk Level", level)
    with col2:
        st.metric("Risk Score", f"{risk.get('risk_score', 0):.2f}")
    with col3:
        st.metric("RUL", f"{risk.get('rul_days', 'N/A')} days")
    with col4:
        st.metric("Criticality", info.get("criticality", "N/A").upper())

    st.divider()

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
        st.markdown("#### 📈 Sensor Trends")
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
                        )
                        st.plotly_chart(fig, use_container_width=True)

        # Anomaly score timeline
        if has_anomaly and "anomaly_score" in df.columns:
            st.markdown("#### 🚨 Anomaly Score Timeline")
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
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No sensor data found for {eid}")

    # ─── Fleet Overview ─────────────────────────────────────
    st.divider()
    st.markdown("#### 🏭 Fleet Health Overview")
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
