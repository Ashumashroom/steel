"""
Log Upload — upload free-text or CSV maintenance log files. The system
auto-extracts which equipment and which agent/category each entry belongs to,
shows a preview, and on confirmation commits to maintenance_logs.csv and
re-indexes RAG.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EQUIPMENT

AGENT_LABELS = {
    "diagnosis": "🔍 Diagnostic Agent",
    "rca": "❓ RCA Agent",
    "prediction": "📈 Predictive Agent",
    "planning": "🛠️ Maintenance Planner",
    "general": "💬 General",
}

SEVERITY_BADGES = {
    "critical": "🔴 Critical",
    "high": "🟠 High",
    "medium": "🟡 Medium",
    "low": "🟢 Low",
}


def render_log_upload():
    """Render the log upload & extraction tab."""
    st.markdown("### 📥 Upload Maintenance Logs")
    st.caption(
        "Upload a plain-text (.txt) or CSV log file. Each entry is automatically "
        "matched to the relevant equipment and routed to the appropriate agent category."
    )

    uploaded_file = st.file_uploader(
        "Drop a log file here",
        type=["txt", "csv"],
        help="One log entry per line for .txt files, or a CSV with maintenance log columns.",
    )

    if uploaded_file is None:
        st.info("No file uploaded yet. Supported formats: .txt, .csv")
        _show_known_equipment()
        return

    from utils.log_ingestor import parse_log_file

    file_bytes = uploaded_file.read()
    entries = parse_log_file(file_bytes, uploaded_file.name)

    if not entries:
        st.warning(
            "No entries could be matched to known equipment. "
            "Make sure each line mentions an equipment ID (e.g. BF-001, RM-003) "
            "or an equipment name (e.g. 'Blast Furnace', 'Rolling Mill')."
        )
        _show_known_equipment()
        return

    st.success(f"✅ Extracted **{len(entries)}** entries from `{uploaded_file.name}`")

    # ─── Preview table ───────────────────────────────────
    preview_rows = []
    for e in entries:
        eq_name = EQUIPMENT.get(e["equipment_id"], {}).get("name", e["equipment_id"])
        preview_rows.append({
            "Equipment": f"{e['equipment_id']} — {eq_name}",
            "Routed to Agent": AGENT_LABELS.get(e["_agent"], e["_agent"]),
            "Fault Code": e["fault_code"],
            "Severity": SEVERITY_BADGES.get(e["severity"], e["severity"]),
            "Downtime (h)": e["downtime_hours"],
            "Description": e["description"],
        })

    preview_df = pd.DataFrame(preview_rows)
    st.markdown("#### Preview — review before committing")
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

    # ─── Summary by equipment / agent ─────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Entries per Equipment**")
        eq_counts = preview_df["Equipment"].value_counts()
        st.bar_chart(eq_counts)
    with col2:
        st.markdown("**Entries per Agent**")
        agent_counts = preview_df["Routed to Agent"].value_counts()
        st.bar_chart(agent_counts)

    st.divider()

    # ─── Commit ────────────────────────────────────────────
    col1, col2 = st.columns([1, 3])
    with col1:
        confirm = st.button("✅ Commit & Re-index", type="primary", use_container_width=True)
    with col2:
        st.caption(
            "This appends the entries above to `maintenance_logs.csv` and re-indexes "
            "the maintenance logs collection in ChromaDB so the agents can use them immediately."
        )

    if confirm:
        from utils.log_ingestor import commit_entries, reindex_logs

        with st.spinner("Committing entries..."):
            n_written = commit_entries(entries)

        with st.spinner("Re-indexing maintenance logs into ChromaDB..."):
            n_chunks = reindex_logs()

        st.success(
            f"Committed {n_written} entries and re-indexed {n_chunks} chunks. "
            "The Maintenance Wizard will now consider these in future queries."
        )
        st.balloons()


def _show_known_equipment():
    """Show the list of equipment IDs/names the extractor can recognize."""
    with st.expander("📋 Recognized equipment IDs & names"):
        rows = [
            {"ID": eid, "Name": info["name"], "Type": info["type"], "Criticality": info["criticality"]}
            for eid, info in EQUIPMENT.items()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(
            "Each log line/row must mention one of these IDs or names "
            "for it to be recognized and routed."
        )