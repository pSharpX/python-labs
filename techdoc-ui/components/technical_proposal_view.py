"""Structured rendering of the technical-functional proposal."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.format import kpi_row

STATUS = {"ready": "✅ Ready", "needs_clarification": "💬 Needs clarification", "failed": "⚠️ Could not be completed"}


def render_technical(tp: dict[str, Any] | None) -> None:
    if not tp:
        st.caption("The technical proposal is produced once requirements are complete.")
        return
    seg, line, svc = tp.get("segment") or {}, tp.get("business_line") or {}, tp.get("requested_service") or {}
    st.markdown(f"**Version {tp['version']}** · {STATUS.get(tp['status'], tp['status'])} · based on requirements v{tp['based_on_requirements_version']}")
    kpi_row([("Segment", seg.get("nombre", "—")), ("Business line", line.get("nombre", "—")),
             ("Catalog service", svc.get("nombre", "—")), ("Duration", f"{(tp.get('duration') or {}).get('total_weeks', '—'):g} weeks"
                                                            if tp.get("duration") else "—")], small=True)

    if tp.get("open_questions"):
        blocking = [q["question"] for q in tp["open_questions"] if q["blocking"]]
        if blocking:
            st.warning("Blocking questions:\n" + "\n".join(f"- {q}" for q in blocking))
    if tp.get("executive_summary"):
        st.markdown(tp["executive_summary"])
    if tp.get("architecture"):
        with st.expander("Architecture", expanded=True):
            st.markdown(tp["architecture"])
            if tp.get("architecture_components"):
                st.dataframe([{"Component": c["name"], "Type": c["component_type"], "Responsibility": c["responsibility"], "Technology": c["technology"]}
                              for c in tp["architecture_components"]], hide_index=True, use_container_width=True)
            if tp.get("technology_stack"):
                st.dataframe([{"Layer": t["layer"], "Technology": t["technology"], "Rationale": t["rationale"],
                               "Basis": "📘 Documented" if t["documented"] else "Recommendation"} for t in tp["technology_stack"]],
                             hide_index=True, use_container_width=True)

    phases = sorted(tp.get("implementation_phases", []), key=lambda p: p["order"])
    if phases:
        st.markdown("**Implementation phases**")
        acts = tp.get("phase_activities", [])
        for ph in phases:
            with st.expander(f"{ph['id']} · {ph['name']} — {ph['duration_weeks']:g} weeks"):
                st.caption(ph.get("objective", ""))
                rows = [{"Activity": f"{a['id']} {a['name']}", "Tasks": "; ".join(a["tasks"]), "Profiles": ", ".join(a["profile_ids"])}
                        for a in acts if a["phase_id"] == ph["id"]]
                if rows:
                    st.dataframe(rows, hide_index=True, use_container_width=True)
                dels = [d for d in tp.get("deliverables", []) if d["phase_id"] == ph["id"]]
                for d in dels:
                    crit = [c["description"] for c in tp.get("acceptance_criteria", []) if c["deliverable_id"] == d["id"]]
                    st.markdown(f"📦 **{d['name']}**" + (f" — acceptance: {'; '.join(crit)}" if crit else ""))

    if tp.get("required_profiles"):
        st.markdown("**Required profiles** (from `obtener_perfiles`)")
        st.dataframe([{"Profile": p["name"], "ID": p["profile_id"], "Seniority": p["seniority"],
                       "Responsibilities": "; ".join(p["responsibilities"])} for p in tp["required_profiles"]],
                     hide_index=True, use_container_width=True)
    with st.expander("Risks, scope, prerequisites and references"):
        if tp.get("risks_and_mitigations"):
            st.dataframe([{"Category": r["category"], "Risk": r["description"], "Mitigation": r["mitigation"]} for r in tp["risks_and_mitigations"]],
                         hide_index=True, use_container_width=True)
        st.markdown("**Out of scope**\n" + "\n".join(f"- {x}" for x in tp.get("out_of_scope", [])))
        st.markdown("**Prerequisites / customer responsibilities**\n" + "\n".join(f"- {x}" for x in tp.get("prerequisites", [])))
        refs = tp.get("documentation_references", [])
        st.markdown("**Microsoft Learn references**")
        st.markdown("\n".join(f"- [{r['title']}]({r['url']})" for r in refs) or "_None_")
        if tp.get("documentation_status"):
            st.caption(tp["documentation_status"])
        if tp.get("validation_issues"):
            st.caption("Notes: " + " · ".join(tp["validation_issues"]))
