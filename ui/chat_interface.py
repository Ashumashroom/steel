"""
Chat interface component for the Maintenance Wizard.
Advanced version: styled message cards, inline file upload (logs/manuals/
queries about an uploaded file), conversational feedback, and stable
message ordering.
"""
import streamlit as st
from pathlib import Path
import sys
import re

sys.path.insert(0, str(Path(__file__).parent.parent))


# Phrases that signal the user is giving feedback on the previous response
# rather than asking a new question.
POSITIVE_FEEDBACK_PATTERNS = [
    r"\bgood\b", r"\bgreat\b", r"\bperfect\b", r"\bthanks?\b", r"\bthank you\b",
    r"\bhelpful\b", r"\bnice\b", r"\bcorrect\b", r"\baccurate\b", r"\bexcellent\b",
    r"\bwell done\b", r"\bawesome\b", r"\bspot on\b", r"\byes that.s right\b",
    r"\bappreciated\b", r"\bmakes sense\b", r"\bthat helps?\b", r"\bsuper\b",
    r"\bgood (job|answer|work)\b",
]
NEGATIVE_FEEDBACK_PATTERNS = [
    r"\bwrong\b", r"\bincorrect\b", r"\bnot right\b", r"\bnot helpful\b",
    r"\bbad answer\b", r"\bthat.s not it\b", r"\bnot accurate\b", r"\buseless\b",
    r"\btry again\b", r"\bdoesn.t (make sense|help)\b", r"\bno that.s wrong\b",
    r"\bthis is wrong\b", r"\bnot quite\b", r"\bnope\b", r"\bnot what i (asked|meant|wanted)\b",
    r"\bdidn.t (answer|help)\b", r"\bmissed the point\b",
]


def _classify_feedback(text: str) -> int | None:
    """Return 1 for positive feedback, -1 for negative, or None if the
    message doesn't look like feedback (i.e. it's a new question)."""
    t = text.strip().lower()

    # Very short messages are more likely to be feedback than a real question
    is_short = len(t.split()) <= 6

    for pat in NEGATIVE_FEEDBACK_PATTERNS:
        if re.search(pat, t):
            return -1
    for pat in POSITIVE_FEEDBACK_PATTERNS:
        if re.search(pat, t):
            return 1

    # Short messages with no "?" and no equipment-ish keywords are likely
    # feedback too (e.g. "ok", "cool", "hmm")
    if is_short and "?" not in t and not re.search(r"\b[a-z]{1,3}-\d{3}\b", t):
        ack_words = {"ok", "okay", "cool", "fine", "hmm", "alright", "got it", "noted"}
        if t in ack_words:
            return 1  # treat neutral acknowledgments as mildly positive, non-blocking

    return None


def render_chat_interface():
    """Render the chat interface tab."""
    st.markdown("### 💬 Maintenance Assistant")
    st.caption("Ask about equipment diagnosis, root cause analysis, predictions, or maintenance planning. "
               "You can also attach a log, manual, or report file, and give feedback right in the chat "
               "(e.g. \"that's wrong\" or \"thanks, that helped\").")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": _welcome_message()}
        ]

    # ─── Render full chat history (stable order) ────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🏭" if msg["role"] == "assistant" else "👤"):
            if msg.get("attachment_name"):
                st.markdown(
                    f'<div class="chat-attachment">📎 Attached: <b>{msg["attachment_name"]}</b></div>',
                    unsafe_allow_html=True,
                )
            if msg.get("is_feedback_ack"):
                st.markdown(f'<div class="feedback-ack">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"], unsafe_allow_html=True)

    # ─── Attached file (persists until cleared) ─────────────
    with st.expander("📎 Attach a file (log, manual, report) to ask about", expanded=False):
        uploaded = st.file_uploader(
            "Upload a .txt, .csv, or .md file",
            type=["txt", "csv", "md"],
            key="chat_file_uploader",
            label_visibility="collapsed",
        )
        if uploaded is not None:
            st.session_state.pending_attachment = {
                "name": uploaded.name,
                "content": _read_uploaded_file(uploaded),
            }
            st.success(f"'{uploaded.name}' attached — it will be included with your next message.")
        if st.session_state.get("pending_attachment"):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.caption(f"Currently attached: **{st.session_state.pending_attachment['name']}**")
            with col2:
                if st.button("Remove", key="remove_attachment"):
                    st.session_state.pending_attachment = None
                    st.rerun()

    # ─── Chat input ──────────────────────────────────────────
    if prompt := st.chat_input("Ask a maintenance question, or share feedback on the last answer..."):
        attachment = st.session_state.pop("pending_attachment", None)

        user_msg = {"role": "user", "content": prompt}
        if attachment:
            user_msg["attachment_name"] = attachment["name"]
            user_msg["attachment_content"] = attachment["content"]
        st.session_state.messages.append(user_msg)

        # ─── Check if this message is feedback on the previous response ──
        feedback_rating = None if attachment else _classify_feedback(prompt)
        last_assistant_msg = _find_last_assistant_response()

        if feedback_rating is not None and last_assistant_msg is not None:
            # Record feedback, respond with a short acknowledgment instead
            # of running the full agent pipeline again.
            last_query = _find_query_before(last_assistant_msg)
            _save_feedback(last_query, last_assistant_msg, feedback_rating)

            if feedback_rating > 0:
                ack = "👍 Thanks for the feedback — glad that helped!"
            else:
                ack = "👎 Thanks for letting me know — I've logged this so it can be reviewed and improved."

            st.session_state.messages.append({
                "role": "assistant", "content": ack, "is_feedback_ack": True,
            })
            st.rerun()

        else:
            # Treat as a new question — run the full agent pipeline
            effective_query = prompt
            if attachment:
                effective_query = (
                    f"{prompt}\n\n--- Attached file: {attachment['name']} ---\n"
                    f"{attachment['content'][:4000]}"  # cap to avoid huge prompts
                )

            fast_mode = st.session_state.get("fast_mode", True)
            with st.spinner("⚡ Analyzing (fast mode)..." if fast_mode else "🔍 Analyzing with multi-agent system..."):
                response = _get_response(effective_query, fast_mode=fast_mode)

            # Add a discoverable, inline feedback prompt after substantive
            # answers (skip it for very short/generic replies like clarifying
            # questions, to avoid being noisy).
            if len(response) > 200:
                response += (
                    "\n\n---\n"
                    '<div class="feedback-prompt">💬 Was this helpful? '
                    'Just reply — e.g. <i>"thanks, that helped"</i> or '
                    '<i>"that\'s not right"</i> — and I\'ll log it as feedback.</div>'
                )

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # ─── Sidebar: speed toggle + sample queries ─────────────
    with st.sidebar:
        st.markdown("### ⚡ Response Speed")
        st.session_state.fast_mode = st.toggle(
            "Fast mode (skip critic revisions)",
            value=st.session_state.get("fast_mode", True),
            help="When on, responses are returned after one pass without the "
                 "critic's revision loop — noticeably faster, slightly less polished.",
        )

        st.markdown("### 💡 Sample Queries")
        samples = [
            "Blast Furnace BF-001 showing unusual vibration readings. What could be wrong?",
            "Perform root cause analysis for bearing failure on RM-001",
            "What is the remaining useful life of Rolling Mill Motor RM-003?",
            "Generate a maintenance plan for BOF-001 for next quarter",
            "Show me the health status of all critical equipment",
        ]
        for s in samples:
            if st.button(s, key=f"sample_{hash(s)}", use_container_width=True):
                fast_mode = st.session_state.get("fast_mode", True)
                st.session_state.messages.append({"role": "user", "content": s})
                with st.spinner("⚡ Analyzing..." if fast_mode else "🔍 Analyzing..."):
                    response = _get_response(s, fast_mode=fast_mode)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()


def _find_last_assistant_response() -> str | None:
    """Find the most recent real assistant response (not a feedback ack
    and not the welcome message)."""
    messages = st.session_state.messages
    # Skip the message we just appended (the user's feedback) — start from -2
    for msg in reversed(messages[:-1]):
        if msg["role"] == "assistant" and not msg.get("is_feedback_ack"):
            return msg["content"]
    return None


def _find_query_before(assistant_content: str) -> str:
    """Find the user query that preceded a given assistant response."""
    messages = st.session_state.messages
    for i, msg in enumerate(messages):
        if msg["role"] == "assistant" and msg["content"] == assistant_content:
            if i - 1 >= 0 and messages[i - 1]["role"] == "user":
                return messages[i - 1]["content"]
    return ""


def _read_uploaded_file(uploaded_file) -> str:
    """Read an uploaded txt/csv/md file as text."""
    try:
        raw = uploaded_file.read()
        return raw.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Could not read file: {e}]"


def _welcome_message() -> str:
    return """Welcome to the **Intelligent Maintenance Wizard** 🏭

I can help you with:
- 🔧 **Diagnosis** — Identify probable faults from symptoms or error codes
- 🔍 **Root Cause Analysis** — Drill down to the fundamental cause of failures
- 📊 **Predictions** — Check equipment health, anomalies, and remaining useful life
- 📋 **Maintenance Planning** — Get prioritized action plans with spare parts info
- ❓ **General Queries** — Ask about SOPs, equipment manuals, or procedures
- 📎 **File Q&A** — Attach a log, manual, or report file and ask questions about it

You can also just tell me what you think of an answer — e.g. _"that's correct, thanks"_ or
_"that's wrong"_ — and I'll log it as feedback.

**Try asking:** _"BF-001 is showing high vibration. What could be wrong?"_"""


def _get_response(query: str, fast_mode: bool = False) -> str:
    """Get response from the LangGraph agent pipeline."""
    try:
        from agents.graph import run_query
        result = run_query(query, fast_mode=fast_mode)
        return result.get("final_response", "I couldn't generate a response. Please try again.")
    except Exception as e:
        return f"**Error:** {str(e)}\n\nPlease check your LLM configuration in `.env` file."


def _save_feedback(query: str, response: str, rating: int):
    try:
        from utils.feedback import save_feedback
        save_feedback(query, "", "", response, rating)
    except Exception:
        pass