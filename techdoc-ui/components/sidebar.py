"""Sidebar: create proposals and navigate existing ones."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from api.client import ApiError, ProposalApiClient

STATUS_ICON = {
    "running": "⏳", "awaiting_user": "💬", "awaiting_approval": "🟡", "rejected": "⛔",
    "completed": "✅", "cancelled": "✖️", "failed": "⚠️",
}


def render_sidebar(client: ProposalApiClient, active: str | None, on_select: Callable[[str | None], None],
                   on_create: Callable[[str, str, str], None], app_title: str) -> None:
    with st.sidebar:
        st.markdown(f"### {app_title}")
        st.caption("Propuestas técnico-funcionales, desde la conversación hasta el documento Word aprobado.")

        with st.expander("➕ Nueva propuesta", expanded=active is None):
            with st.form("new_proposal", clear_on_submit=True):
                title = st.text_input("Título de la propuesta", placeholder="e.g. ERP order integration")
                customer = st.text_input("Cliente", placeholder="e.g. Contoso Retail")
                need = st.text_area("Describe la necesidad del negocio", height=140,
                                    placeholder="¿Qué problema debemos resolver? ¿Qué sistemas, usuarios y volúmenes están involucrados?")
                if st.form_submit_button("Iniciar", type="primary", use_container_width=True):
                    if not title.strip() or not need.strip():
                        st.warning("El título y la necesidad del negocio son obligatorios.")
                    else:
                        on_create(title.strip(), customer.strip(), need.strip())

        st.markdown("#### Propuestas")
        try:
            items = client.list_proposals()
        except ApiError as exc:
            st.error(str(exc))
            if st.button("Reintentar", key="retry_list"):
                st.rerun()
            return
        if not items:
            st.caption("Aún no hay propuestas.")
        for p in items:
            icon = STATUS_ICON.get("running" if p.run_state == "running" else p.workflow_status, "•")
            label = f"{icon} {p.title}" + (f" — {p.customer_name}" if p.customer_name else "")
            if st.button(label, key=f"sel_{p.proposal_id}", use_container_width=True,
                         type="primary" if p.proposal_id == active else "secondary",
                         help=f"{p.proposal_id} · {p.workflow_status.replace('_', ' ')} · updated {p.updated_at:%Y-%m-%d %H:%M}"):
                on_select(p.proposal_id)
