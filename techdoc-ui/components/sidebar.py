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
        st.caption("Technical-functional proposals, from conversation to approved Word document.")

        with st.expander("➕ New proposal", expanded=active is None):
            with st.form("new_proposal", clear_on_submit=True):
                title = st.text_input("Proposal title", placeholder="e.g. ERP order integration")
                customer = st.text_input("Customer", placeholder="e.g. Contoso Retail")
                need = st.text_area("Describe the business need", height=140,
                                    placeholder="What problem should we solve? Which systems, users and volumes are involved?")
                if st.form_submit_button("Start proposal", type="primary", use_container_width=True):
                    if not title.strip() or not need.strip():
                        st.warning("Title and business need are required.")
                    else:
                        on_create(title.strip(), customer.strip(), need.strip())

        st.markdown("#### Proposals")
        try:
            items = client.list_proposals()
        except ApiError as exc:
            st.error(str(exc))
            if st.button("Retry", key="retry_list"):
                st.rerun()
            return
        if not items:
            st.caption("No proposals yet.")
        for p in items:
            icon = STATUS_ICON.get("running" if p.run_state == "running" else p.workflow_status, "•")
            label = f"{icon} {p.title}" + (f" — {p.customer_name}" if p.customer_name else "")
            if st.button(label, key=f"sel_{p.proposal_id}", use_container_width=True,
                         type="primary" if p.proposal_id == active else "secondary",
                         help=f"{p.proposal_id} · {p.workflow_status.replace('_', ' ')} · updated {p.updated_at:%Y-%m-%d %H:%M}"):
                on_select(p.proposal_id)
