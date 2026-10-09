"""Conversation rendering. The backend message log is the source of truth."""

from __future__ import annotations

import streamlit as st

from api.schemas import Message

KIND_LABEL = {
    "clarification": "Question", "status": "Update", "approval": "Approval needed",
    "document": "Document", "error": "Problem", "decision": "Decision",
}
AVATAR = {"user": "🧑‍💼", "assistant": "🤖"}


def render_messages(messages: list[Message]) -> None:
    if not messages:
        st.info("Describe the business need to get started.")
    for m in messages:
        role = "user" if m.role == "user" else "assistant"
        with st.chat_message(role, avatar=AVATAR[role]):
            label = KIND_LABEL.get(m.kind)
            if label and role == "assistant":
                st.markdown(f'<div class="ps-kind">{label}</div>', unsafe_allow_html=True)
            st.markdown(m.content)


def chat_placeholder(awaiting: str | None, workflow_status: str) -> str:
    if workflow_status == "completed":
        return "Request a change to scope or requirements (a new version will need approval)…"
    if awaiting == "approval":
        return "Ask a question or change requirements — or use the approval panel…"
    if awaiting == "clarification":
        return "Answer the questions above…"
    return "Type a message…"
