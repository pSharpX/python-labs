"""Conversation rendering. The backend message log is the source of truth."""

from __future__ import annotations

import streamlit as st

from api.schemas import Message

KIND_LABEL = {
    "clarification": "Pregunta", "status": "Actualizar", "approval": "Approval needed",
    "document": "Documento", "error": "Problema", "decision": "Decisión",
}
AVATAR = {"user": "🧑‍💼", "assistant": "🤖"}


def render_messages(messages: list[Message]) -> None:
    if not messages:
        st.info("Describe la necesidad del negocio para comenzar.")
    for m in messages:
        role = "user" if m.role == "user" else "assistant"
        with st.chat_message(role, avatar=AVATAR[role]):
            label = KIND_LABEL.get(m.kind)
            if label and role == "assistant":
                st.markdown(f'<div class="ps-kind">{label}</div>', unsafe_allow_html=True)
            st.markdown(m.content)


def chat_placeholder(awaiting: str | None, workflow_status: str) -> str:
    if workflow_status == "completed":
        return "Solicita un cambio en el alcance o los requisitos (la nueva versión deberá ser aprobada)…"
    if awaiting == "approval":
        return "Haz una pregunta o modifica los requisitos, o utiliza el panel de aprobación…"
    if awaiting == "clarification":
        return "Responde las preguntas anteriores…"
    return "Escribe un mensaje…"
