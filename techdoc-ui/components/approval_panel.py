"""Approval panel shown while the backend is paused at the human-approval stage."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st

from api.schemas import ProposalSummary
from components.format import hours, money

Decide = Callable[[str, int, str | None], None]


def render_approval_panel(summary: ProposalSummary, estimate: dict[str, Any] | None, on_decide: Decide) -> None:
    if summary.awaiting != "approval" or not summary.estimate or summary.is_running:
        return
    head = summary.estimate
    cur = head.currency
    st.markdown('<div class="ps-card ps-approval"><h4>Estimate awaiting your approval</h4>'
                f'<span class="ps-sub">Version {head.version} — nothing is approved until you decide.</span></div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="ps-kpi-label">Total investment</div><div class="ps-kpi">{money(head.total_cost, cur)}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="ps-kpi-label">Effort</div><div class="ps-kpi">{hours(head.total_hours)} h</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="ps-kpi-label">Duration</div><div class="ps-kpi" style="font-size:1.15rem">{head.estimated_duration or "—"}</div>',
                unsafe_allow_html=True)
    if estimate and estimate.get("commercial_assumptions"):
        st.markdown("**Key assumptions:** " + " · ".join(estimate["commercial_assumptions"][:5]))
    if estimate and estimate.get("validation_warnings"):
        st.caption("⚠️ " + " · ".join(estimate["validation_warnings"]))

    feedback = st.text_area("Feedback (required to request changes or reject)", key=f"fb_{summary.proposal_id}_{head.version}",
                            placeholder="e.g. Reduce QA effort; assume the customer provides test data…", height=80)
    b1, b2, b3 = st.columns([1, 1, 1])
    if b1.button("✅ Approve estimate", type="primary", use_container_width=True, key=f"approve_{head.version}"):
        on_decide("approve", head.version, feedback or None)
    if b2.button("✏️ Request changes", use_container_width=True, key=f"changes_{head.version}"):
        if not feedback.strip():
            st.warning("Describe the changes you need.")
        else:
            on_decide("request_changes", head.version, feedback)
    if b3.button("⛔ Reject", use_container_width=True, key=f"reject_{head.version}"):
        if not feedback.strip():
            st.warning("Please give a reason for the rejection.")
        else:
            on_decide("reject", head.version, feedback)
    with st.expander("Cancel this proposal"):
        st.caption("Cancelling stops the workflow. History and artifacts are kept for audit.")
        if st.button("Cancel workflow", key=f"cancel_{head.version}"):
            on_decide("cancel", head.version, feedback or None)
