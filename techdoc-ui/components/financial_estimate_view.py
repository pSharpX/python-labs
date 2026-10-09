"""Structured rendering of the financial estimate."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.format import hours, kpi_row, money, pct

__all__ = ["hours", "money", "render_estimate"]


def render_estimate(est: dict[str, Any] | None) -> None:
    if not est:
        st.caption("The estimate is calculated after the technical proposal is ready.")
        return
    cur = est["currency"]
    st.markdown(f"**Version {est['version']}** · approval: **{est['approval_status'].replace('_', ' ')}** · "
                f"based on technical proposal v{est['based_on_technical_version']}")
    if est.get("validation_errors"):
        st.error("This estimate failed validation:\n" + "\n".join(f"- {e}" for e in est["validation_errors"]))
    kpi_row([("Total", money(est["total_cost"], cur)), ("Effort", f"{hours(est['total_hours'])} h"),
             ("Duration", est.get("estimated_duration") or "—"), ("Confidence", est["confidence_level"].title())], small=True)

    rows = [["Subtotal", money(est["subtotal"], cur)]]
    for key in ("contingency", "discount", "taxes"):
        adj = est.get(key)
        if adj and adj["applied"]:
            rows.append([f"{adj['label']} ({pct(adj['rate'])})", ("− " if key == "discount" else "") + money(adj["amount"], cur)])
    rows.append(["Total", money(est["total_cost"], cur)])
    st.dataframe([{"Concept": a, "Amount": b} for a, b in rows], hide_index=True, use_container_width=True)
    st.caption(f"Formula: {est['formula']}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**By phase**")
        st.dataframe([{"Phase": p["phase_name"], "Hours": hours(p["hours"]), "Amount": money(p["amount"], cur)} for p in est["phase_estimates"]],
                     hide_index=True, use_container_width=True)
    with c2:
        st.markdown("**By profile**")
        st.dataframe([{"Profile": p["profile_name"], "Hours": hours(p["hours"]), "Rate": money(p["hourly_rate"], cur),
                       "Amount": money(p["amount"], cur)} for p in est["profile_estimates"]], hide_index=True, use_container_width=True)
    with st.expander("Detailed breakdown by activity"):
        st.dataframe([{"Phase": li["phase_name"], "Activity": f"{li['activity_id']} {li['activity_name']}", "Profile": li["profile_name"],
                       "Hours": hours(li["hours"]), "Rate": money(li["hourly_rate"], cur), "Amount": money(li["amount"], cur),
                       "Rationale": li.get("rationale", "")} for li in est["activity_estimates"]],
                     hide_index=True, use_container_width=True)
    with st.expander("Assumptions and exclusions"):
        st.markdown("**Commercial assumptions**\n" + ("\n".join(f"- {a}" for a in est["commercial_assumptions"]) or "_None_"))
        st.markdown("**Exclusions**\n" + ("\n".join(f"- {a}" for a in est["exclusions"]) or "_None_"))
        if est.get("validation_warnings"):
            st.caption("Warnings: " + " · ".join(est["validation_warnings"]))
        st.caption(f"Rate card: {est.get('rate_card_source') or '—'}")
