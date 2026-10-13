"""Proposal Studio — Streamlit chat client for the proposal workflow API.

Run:  streamlit run app.py   (from the frontend/ folder, with the backend running)
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import streamlit as st

from api.client import ApiError, ProposalApiClient
from api.schemas import ProposalSummary
from components.approval_panel import render_approval_panel
from components.chat import chat_placeholder, render_messages
from components.document_panel import render_document_panel, render_versions
from components.financial_estimate_view import render_estimate
from components.requirements_view import render_requirements
from components.sidebar import render_sidebar
from components.technical_proposal_view import render_technical
from components.workflow_status import RUNNING_TEXT, render_header
from config import get_settings
from state import init_session, restore_session, set_active

settings = get_settings()
st.set_page_config(page_title=settings.app_title, page_icon="📑", layout="wide", initial_sidebar_state="expanded")
st.markdown(f"<style>{(Path(__file__).parent / 'styles' / 'theme.css').read_text()}</style>", unsafe_allow_html=True)


@st.cache_resource
def get_client() -> ProposalApiClient:
    return ProposalApiClient(settings)


client = get_client()
init_session(st.session_state)
if (warning := restore_session(st.session_state, st.query_params, client)) is not None:
    st.session_state.flash = ("warning", warning)


# ---- actions ------------------------------------------------------------------------------


def wait_for_backend(pid: str) -> ProposalSummary | None:
    """Show progress while the backend works, then return the settled summary."""
    with st.status("Working on it…", expanded=False) as status:
        def tick(s: ProposalSummary) -> None:
            status.update(label=RUNNING_TEXT.get(s.current_stage, "Working…"))

        summary = client.wait_until_idle(pid, on_tick=tick)
        if summary.is_running:
            status.update(label="Still working — this can take a few minutes. Refresh to check progress.", state="running")
        elif summary.workflow_status == "failed":
            status.update(label="A step failed", state="error")
        else:
            status.update(label="Done", state="complete")
    return summary


def perform(action: Callable[[], ProposalSummary], description: str) -> None:
    try:
        summary = action()
        set_active(st.session_state, st.query_params, summary.proposal_id)
        wait_for_backend(summary.proposal_id)
        st.session_state.pop("last_failed", None)
    except ApiError as exc:
        st.session_state.flash = ("error", f"{description} failed: {exc}")
        if exc.retryable:
            st.session_state.last_failed = (action, description)
    st.rerun()


def select(pid: str | None) -> None:
    set_active(st.session_state, st.query_params, pid)
    st.rerun()


def create(title: str, customer: str, need: str) -> None:
    perform(lambda: client.create_proposal(title, customer, need), "Creando la propuesta")


# ---- layout -------------------------------------------------------------------------------

active = st.session_state.active_proposal
render_sidebar(client, active, select, create, settings.app_title)

if st.session_state.flash:
    level, text = st.session_state.flash
    getattr(st, level)(text)
    st.session_state.flash = None
    if failed := st.session_state.get("last_failed"):
        if st.button("↻ Reintentar"):
            perform(*failed)

if not active:
    st.markdown(f"## Bienvenido a {settings.app_title}")
    st.markdown(
        "Describe en lenguaje sencillo las necesidades de negocio de tu cliente. El asistente te ayudará a:\n\n"
        "1. **Definir y validar los requerimientos** hasta que estén completos y listos para avanzar\n"
        "2. **Diseñar la solución técnica** utilizando nuestro catálogo de servicios y la documentación oficial de Microsoft Learn.\n"
        "3. **Estimar el esfuerzo y los costos** con base a nuestro tarifario autorizado.\n"
        "4. **Revisar y aprobar la propuesta**: nada se aprobará sin tu autorización explícita.\n"
        "5. **Generar una propuesta profesional en Word**, lista para descargar y compartir.\n\n"
        "Para comenzar, selecciona **➕ Nueva propuesta** en la barra lateral."
    )

    try:
        h = client.health()
        st.caption(f"Service online · API v{h['version']} · Microsoft Learn {'connected' if h['mcp_available'] else 'unavailable: ' + str(h.get('mcp_detail'))}")
    except ApiError as exc:
        st.error(str(exc))
    st.stop()

try:
    summary = client.get_proposal(active)
except ApiError as exc:
    st.error(str(exc))
    c1, c2 = st.columns(2)
    if c1.button("↻ Reintentar"):
        st.rerun()
    if c2.button("Cerrar propuesta"):
        select(None)
    st.stop()

if summary.is_running:  # e.g. page refreshed mid-run
    render_header(summary)
    wait_for_backend(summary.proposal_id)
    st.rerun()

render_header(summary)
try:
    messages = client.messages(active)
    versions = client.versions(active)
    requirements = client.artifact(active, "requirements")
    technical = client.artifact(active, "technical-proposal")
    estimate = client.artifact(active, "estimate")
except ApiError as exc:
    st.error(f"No se pudieron cargar los detalles de la propuesta.: {exc}")
    if st.button("↻ Reintentar la carga"):
        st.rerun()
    st.stop()

left, right = st.columns([5, 6], gap="large")

with left:
    st.markdown("#### Conversación")
    with st.container(height=620, border=True):
        render_messages(messages)

with right:
    render_approval_panel(
        summary, estimate,
        lambda decision, version, fb: perform(lambda: client.decide(active, decision, version, fb), "Submitting your decision"),
    )

    if summary.workflow_status == "failed":
        st.error(f"El último paso falló. Tu progreso está guardado. {summary.last_error or ''}")
        if st.button("↻ Reintentar el paso fallido", type="primary"):
            perform(lambda: client.resume(active, "retry"), "Retrying")
    elif summary.awaiting == "clarification" and summary.current_stage in ("technical_design", "financial_estimation"):
        st.markdown('<div class="ps-banner warn">El proceso está en pausa. Responde en el chat o vuelve a intentar el paso  '
                    'después de solucionar el problema (e.g. catalog or rate configuration) .</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("↻ Reintentar este paso", use_container_width=True):
            perform(lambda: client.resume(active, "retry"), "Reintentando...")
        if c2.button("Cancelar workflow", use_container_width=True):
            perform(lambda: client.resume(active, "cancel"), "Cancelando...")
    elif summary.workflow_status == "rejected":
        st.markdown('<div class="ps-banner warn">La estimación fue rechazada. Describe en el chat qué se debe cambiar, '
                    'o volver a estimar tal como está.</div>', unsafe_allow_html=True)
        if st.button("↻ Volver a estimar"):
            perform(lambda: client.resume(active, "retry"), "Reestimando...")

    render_document_panel(client, summary, versions)

    tabs = st.tabs(["📋 Requerimientos", "🏗️ Solución", "💰 Estimación", "🕘 Versiones"])
    with tabs[0]:
        render_requirements(requirements)
    with tabs[1]:
        render_technical(technical)
    with tabs[2]:
        render_estimate(estimate)
    with tabs[3]:
        render_versions(versions)

disabled = summary.is_running or summary.workflow_status == "cancelled"
if prompt := st.chat_input(chat_placeholder(summary.awaiting, summary.workflow_status), disabled=disabled):
    perform(lambda: client.send_message(active, prompt), "Enviando tu mensaje")
