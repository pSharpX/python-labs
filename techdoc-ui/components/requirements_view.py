"""Structured rendering of the requirements specification."""

from __future__ import annotations

from typing import Any

import streamlit as st

STATUS = {"ready": "✅ Ready for architecture", "awaiting_user": "💬 Waiting for your answers",
          "in_progress": "⏳ In progress", "invalid": "⚠️ Not enough information yet"}


def _bullets(items: list[str]) -> None:
    st.markdown("\n".join(f"- {i}" for i in items) if items else "_None recorded._")


def render_requirements(req: dict[str, Any] | None) -> None:
    if not req:
        st.caption("Requirements will appear here once the analyst has processed your first message.")
        return
    st.markdown(f"**Version {req['version']}** · {STATUS.get(req['status'], req['status'])} · category `{req.get('service_category', '')}`")
    if req.get("change_summary"):
        st.caption(f"Latest change: {req['change_summary']}")
    if req.get("business_problem"):
        st.markdown(f"**Business problem.** {req['business_problem']}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Objectives**")
        _bullets(req.get("objectives", []))
    with c2:
        st.markdown("**Expected outcomes**")
        _bullets(req.get("expected_outcomes", []))

    reqs = [{"ID": r["id"], "Requirement": r["description"], "Priority": r["priority"].upper(), "Source": r["source"]}
            for r in req.get("functional_requirements", []) + req.get("non_functional_requirements", [])]
    if reqs:
        st.markdown("**Functional and non-functional requirements**")
        st.dataframe(reqs, hide_index=True, use_container_width=True)
    if req.get("integrations"):
        st.markdown("**Integrations**")
        st.dataframe([{"System": i["system"], "Purpose": i["purpose"], "Direction": i["direction"], "Method": i["protocol_or_method"]}
                      for i in req["integrations"]], hide_index=True, use_container_width=True)
    vol = req.get("data_and_volumetrics") or {}
    if any(vol.values()):
        st.markdown(f"**Volumetrics.** Sources: {', '.join(vol.get('data_sources', [])) or '—'} · "
                    f"Data: {vol.get('data_volumes') or '—'} · Transactions: {vol.get('transaction_volumes') or '—'}")
    scope = req.get("scope") or {}
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**In scope**")
        _bullets(scope.get("in_scope", []))
    with c2:
        st.markdown("**Out of scope**")
        _bullets(scope.get("out_of_scope", []))
    with st.expander("Assumptions, constraints, risks and open items"):
        st.markdown("**Assumptions**")
        _bullets(req.get("assumptions", []))
        st.markdown("**Constraints**")
        _bullets(req.get("constraints", []))
        st.markdown("**Risks**")
        _bullets([r["description"] for r in req.get("risks", [])])
        gaps = req.get("missing_information", [])
        st.markdown("**Missing information**")
        _bullets([f"{'🔴 ' if g['blocking'] else ''}{g['topic']} — {g['reason']}" for g in gaps])
        if req.get("validation_issues"):
            st.markdown("**Validation issues**")
            _bullets(req["validation_issues"])
