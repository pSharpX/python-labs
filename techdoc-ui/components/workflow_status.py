"""Header and stage stepper."""

from __future__ import annotations

import html

import streamlit as st

from api.schemas import ProposalSummary

STEPS = [
    ("requirements", "Requirements", "requirements"),
    ("technical_design", "Technical design", "technical_proposal"),
    ("financial_estimation", "Financial estimate", "financial_estimate"),
    ("approval", "Approval", None),
    ("document_generation", "Document", "document"),
]
STAGE_INDEX = {key: i for i, (key, _, _) in enumerate(STEPS)} | {"completed": len(STEPS)}

STATUS_LABEL = {
    "running": ("Working", "run"),
    "awaiting_user": ("Needs your input", "warn"),
    "awaiting_approval": ("Awaiting approval", "warn"),
    "rejected": ("Estimate rejected", "bad"),
    "completed": ("Completed", "ok"),
    "cancelled": ("Cancelled", "bad"),
    "failed": ("Step failed", "bad"),
}

RUNNING_TEXT = {
    "requirements": "Analysing requirements…",
    "technical_design": "Designing the technical solution…",
    "financial_estimation": "Estimating effort and cost…",
    "approval": "Recording your decision…",
    "document_generation": "Generating the Word document…",
    "completed": "Finishing…",
}


def status_pill(summary: ProposalSummary) -> str:
    key = "running" if summary.is_running else summary.workflow_status
    label, cls = STATUS_LABEL.get(key, (key.replace("_", " ").title(), ""))
    return f'<span class="ps-pill {cls}">{html.escape(label)}</span>'


def step_states(summary: ProposalSummary) -> list[tuple[str, str, str]]:
    """Return (label, css_class, sub_text) per step. Pure function for testability."""
    current = STAGE_INDEX.get(summary.current_stage, 0)
    if summary.workflow_status == "completed":
        current = len(STEPS)
    elif summary.workflow_status == "awaiting_approval" and not summary.is_running:
        current = STAGE_INDEX["approval"]
    versions = summary.artifact_versions.model_dump()
    out = []
    for i, (_, label, artifact) in enumerate(STEPS):
        version = versions.get(artifact) if artifact else (summary.estimate.version if summary.estimate else None)
        stale = artifact in summary.stale_artifacts if artifact else "approval" in summary.stale_artifacts
        if i < current:
            cls, sub = "done", f"v{version}" if version else "Done"
            if label == "Approval":
                sub = summary.approval_status.replace("_", " ").title()
        elif i == current:
            if summary.is_running:
                cls, sub = "active", "In progress…"
            elif summary.workflow_status in ("awaiting_user", "rejected", "failed"):
                cls, sub = "blocked", {"awaiting_user": "Needs your input", "rejected": "Rejected", "failed": "Failed — retry"}[summary.workflow_status]
            elif summary.workflow_status == "awaiting_approval":
                cls, sub = "blocked", "Your decision"
            else:
                cls, sub = "active", "Current"
        else:
            cls, sub = "", "Pending"
        if stale and i <= current:
            cls, sub = f"{cls} stale", "Needs regeneration"
        out.append((label, cls, sub))
    return out


def render_header(summary: ProposalSummary) -> None:
    customer = f" · {html.escape(summary.customer_name)}" if summary.customer_name else ""
    st.markdown(
        f'<div class="ps-header"><div><p class="ps-title">{html.escape(summary.title)}</p>'
        f'<span class="ps-sub">{summary.proposal_id}{customer} · revision {summary.revision_number}</span></div>'
        f"<div>{status_pill(summary)}</div></div>",
        unsafe_allow_html=True,
    )
    cells = "".join(
        f'<div class="ps-step {cls}"><div class="n">Step {i + 1}</div><div class="l">{label}</div><div class="s">{sub}</div></div>'
        for i, (label, cls, sub) in enumerate(step_states(summary))
    )
    st.markdown(f'<div class="ps-steps">{cells}</div>', unsafe_allow_html=True)
    if summary.stale_artifacts:
        items = ", ".join(s.replace("_", " ") for s in summary.stale_artifacts)
        st.markdown(f'<div class="ps-banner info">Changed since the last approved version — still to regenerate or re-approve: <b>{items}</b>.</div>',
                    unsafe_allow_html=True)
