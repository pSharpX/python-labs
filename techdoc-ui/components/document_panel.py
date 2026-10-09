"""Document summary, download and version history."""

from __future__ import annotations

import streamlit as st

from api.client import ApiError, ProposalApiClient
from api.schemas import ProposalSummary, Versions


def _download(client: ProposalApiClient, pid: str, version: int, primary: bool) -> None:
    key = f"docbytes_{pid}_{version}"
    if key not in st.session_state:
        try:
            st.session_state[key] = client.download_document(pid, version)
        except ApiError as exc:
            st.error(f"Could not fetch document v{version}: {exc}")
            return
    data, filename = st.session_state[key]
    st.download_button(f"⬇️ Download v{version} (.docx)", data=data, file_name=filename, key=f"dl_{pid}_{version}",
                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       type="primary" if primary else "secondary", use_container_width=primary)


def render_document_panel(client: ProposalApiClient, summary: ProposalSummary, versions: Versions | None) -> None:
    docs = versions.documents if versions else []
    if not docs:
        return
    latest = docs[-1]
    current = summary.has_document and "document" not in summary.stale_artifacts
    title = "Approved proposal document" if current else "Previously approved document"
    st.markdown(f'<div class="ps-card"><h4>📄 {title}</h4>'
                f'<span class="ps-sub">Version {latest["document_version"]} · estimate v{latest["estimate_version"]} · '
                f'technical v{latest["technical_version"]} · generated {latest["created_at"][:16].replace("T", " ")} UTC · '
                f'sha256 {latest["content_hash"][:12]}…</span></div>', unsafe_allow_html=True)
    if not current:
        st.caption("The proposal has changed since this document was approved. A new document is issued after the new estimate is approved.")
    _download(client, summary.proposal_id, latest["document_version"], primary=current)
    if len(docs) > 1:
        with st.expander("Earlier document versions"):
            for d in reversed(docs[:-1]):
                _download(client, summary.proposal_id, d["document_version"], primary=False)


def render_versions(versions: Versions | None) -> None:
    if not versions:
        return
    st.markdown("**Artifact versions**")
    st.dataframe([{"Artifact": a["artifact_type"].replace("_", " "), "Version": a["version"], "Status": a.get("status") or "",
                   "Fingerprint": a["fingerprint"], "Created (UTC)": a["created_at"][:19].replace("T", " ")}
                  for a in versions.artifacts], hide_index=True, use_container_width=True)
    st.markdown("**Approval decisions**")
    if versions.approvals:
        st.dataframe([{"Decision": a["decision"].replace("_", " "), "Estimate": f"v{a['estimate_version']}",
                       "Technical": f"v{a['technical_version']}", "By": a["user_id"], "At (UTC)": a["decided_at"][:19].replace("T", " "),
                       "Feedback": a.get("feedback") or ""} for a in versions.approvals], hide_index=True, use_container_width=True)
    else:
        st.caption("No decisions recorded yet.")
