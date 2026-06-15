"""
Equipment Manager UI — view, add, edit, and delete equipment dynamically.
New machines automatically get a generated manual, synthetic sensor data,
RAG indexing, and trained analytics models — no restart required.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_equipment, SENSOR_PARAMS
from utils.equipment_manager import (
    add_equipment, update_equipment, delete_equipment,
    reindex_manual, VALID_TYPES, VALID_CRITICALITY,
)

CRITICALITY_BADGES = {
    "critical": "🔴 Critical",
    "high": "🟠 High",
    "medium": "🟡 Medium",
    "low": "🟢 Low",
}


def render_equipment_manager():
    """Render the Equipment Manager (CRUD) tab."""
    st.markdown("### 🏭 Equipment Manager")
    st.caption(
        "Add or remove equipment dynamically. New machines automatically get a "
        "generated manual, synthetic sensor data, RAG indexing, and trained analytics models."
    )

    registry = get_equipment()

    # ─── Current Fleet ───────────────────────────────────────
    st.markdown("#### Current Fleet")
    if registry:
        rows = []
        for eid, info in registry.items():
            rows.append({
                "ID": eid,
                "Name": info["name"],
                "Type": info["type"],
                "Criticality": CRITICALITY_BADGES.get(info["criticality"], info["criticality"]),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.metric("Total Equipment", len(registry))
    else:
        st.info("No equipment registered yet.")

    st.divider()

    # ─── Add New Machine ───────────────────────────────────────
    st.markdown("#### ➕ Add New Machine")
    with st.form("add_equipment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input(
                "Equipment ID",
                placeholder="e.g. BF-003",
                help="Format: 2-3 letter prefix + dash + number, e.g. BF-003, RM-004",
            )
            new_name = st.text_input("Display Name", placeholder="e.g. Blast Furnace #3")
        with col2:
            new_type = st.selectbox("Equipment Type", VALID_TYPES)
            new_criticality = st.selectbox("Criticality", VALID_CRITICALITY, index=2)

        generate_files = st.checkbox(
            "Auto-generate manual + synthetic sensor data + index into RAG",
            value=True,
            help="Recommended — makes the new machine immediately usable by all agents.",
        )

        submitted = st.form_submit_button("Add Machine", type="primary", use_container_width=True)

    if submitted:
        if not new_id or not new_name:
            st.error("Equipment ID and Display Name are required.")
        else:
            with st.spinner(f"Adding {new_id}..."):
                success, message = add_equipment(
                    new_id, new_name, new_type, new_criticality,
                    generate_files=generate_files,
                )

                if success and generate_files:
                    # Re-index the new manual into ChromaDB
                    try:
                        n_chunks = reindex_manual(new_id.strip().upper())
                        message += f" Indexed {n_chunks} manual chunks into RAG."
                    except Exception as e:
                        message += f" (RAG indexing skipped: {e})"

                    # Train analytics models for the new machine
                    try:
                        from analytics.anomaly_detector import refresh_detector_for
                        from analytics.rul_predictor import refresh_predictor_for
                        refresh_detector_for(new_id.strip().upper())
                        refresh_predictor_for(new_id.strip().upper())
                        message += " Anomaly + RUL models trained."
                    except Exception as e:
                        message += f" (Analytics training skipped: {e})"

            if success:
                st.success(message)
                st.balloons()
                st.rerun()
            else:
                st.error(message)

    st.divider()

    # ─── Edit / Delete Existing Machine ─────────────────────────
    st.markdown("#### ✏️ Edit or Delete Machine")
    if not registry:
        st.info("No equipment to edit.")
        return

    eq_options = {f"{eid} — {info['name']}": eid for eid, info in registry.items()}
    selected_label = st.selectbox("Select Equipment", list(eq_options.keys()), key="edit_select")
    selected_eid = eq_options[selected_label]
    selected_info = registry[selected_eid]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Update Details")
        with st.form("edit_equipment_form"):
            edit_name = st.text_input("Display Name", value=selected_info["name"])
            edit_criticality = st.selectbox(
                "Criticality", VALID_CRITICALITY,
                index=VALID_CRITICALITY.index(selected_info["criticality"])
                if selected_info["criticality"] in VALID_CRITICALITY else 2,
            )
            st.caption(f"Type: **{selected_info['type']}** (immutable)")
            update_submitted = st.form_submit_button("Save Changes", use_container_width=True)

        if update_submitted:
            success, message = update_equipment(selected_eid, name=edit_name, criticality=edit_criticality)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        st.markdown("##### Danger Zone")
        st.warning(
            f"Deleting **{selected_eid}** removes it from the registry and deletes its "
            "generated manual + sensor data files. This cannot be undone."
        )
        delete_files = st.checkbox("Also delete generated manual & sensor files", value=True, key="del_files")
        confirm_delete = st.checkbox(f"I understand — permanently delete {selected_eid}", key="confirm_del")

        if st.button("🗑️ Delete Machine", type="primary", disabled=not confirm_delete, use_container_width=True):
            success, message = delete_equipment(selected_eid, delete_files=delete_files)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)