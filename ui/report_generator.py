"""
Report Generator — structured maintenance reports.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LOGS_DIR, get_equipment


def render_report_generator():
    """Render the reports tab."""
    st.markdown("### 📋 Maintenance Reports")

    report_type = st.selectbox("Report Type", [
        "Equipment Health Summary",
        "Maintenance Log History",
        "Risk Assessment Report",
    ])

    if report_type == "Equipment Health Summary":
        _render_health_summary()
    elif report_type == "Maintenance Log History":
        _render_log_history()
    elif report_type == "Risk Assessment Report":
        _render_risk_report()


def _render_health_summary():
    """Generate equipment health summary report."""
    st.markdown("#### Equipment Health Summary Report")
    st.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        from analytics.risk_classifier import get_all_risk_levels
        risks = get_all_risk_levels()

        report_lines = [
            f"# Equipment Health Summary Report",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Equipment:** {len(get_equipment())}",
            "",
        ]

        critical_count = sum(1 for r in risks if r["risk_level"] == "critical")
        high_count = sum(1 for r in risks if r["risk_level"] == "high")
        report_lines.append(f"**Critical Alerts:** {critical_count}")
        report_lines.append(f"**High Risk:** {high_count}")
        report_lines.append("")

        for r in risks:
            report_lines.append(
                f"### {r['equipment_name']} ({r['equipment_id']})\n"
                f"- **Risk Level:** {r['risk_level'].upper()}\n"
                f"- **Risk Score:** {r['risk_score']:.3f}\n"
                f"- **RUL:** {r.get('rul_days', 'N/A')} days\n"
                f"- **Urgency:** {r['urgency']}\n"
            )

        report_text = "\n".join(report_lines)
        st.markdown(report_text)

        st.download_button(
            "📥 Download Report (Markdown)",
            report_text,
            file_name=f"health_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
        )
    except Exception as e:
        st.error(f"Error generating report: {e}")


def _render_log_history():
    """Show maintenance log history."""
    csv_path = LOGS_DIR / "maintenance_logs.csv"
    if not csv_path.exists():
        st.warning("No maintenance logs found. Run data generator first.")
        return

    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        eq_filter = st.multiselect("Equipment", sorted(df["equipment_id"].unique()))
    with col2:
        sev_filter = st.multiselect("Severity", sorted(df["severity"].unique()))

    if eq_filter:
        df = df[df["equipment_id"].isin(eq_filter)]
    if sev_filter:
        df = df[df["severity"].isin(sev_filter)]

    st.dataframe(
        df.sort_values("timestamp", ascending=False).head(100),
        use_container_width=True, hide_index=True,
    )

    st.metric("Total Records", len(df))
    st.metric("Total Downtime (hours)", f"{df['downtime_hours'].sum():,.1f}")


def _render_risk_report():
    """Generate detailed risk assessment report."""
    try:
        from analytics.risk_classifier import get_all_risk_levels
        risks = get_all_risk_levels()

        data = []
        for r in risks:
            bd = r.get("breakdown", {})
            data.append({
                "Equipment": f"{r['equipment_id']}",
                "Name": r["equipment_name"],
                "Risk Level": r["risk_level"].upper(),
                "Score": r["risk_score"],
                "Anomaly Risk": bd.get("anomaly_risk", 0),
                "RUL Risk": bd.get("rul_risk", 0),
                "History Risk": bd.get("history_risk", 0),
                "Urgency": r["urgency"],
            })

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error: {e}")