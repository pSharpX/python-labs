"""Session-state helpers (pure functions so they can be unit-tested without Streamlit).

The active proposal id is mirrored into the URL query string (``?proposal=...``) so a
page refresh or reconnect restores the same proposal. The backend stays authoritative:
on restore we re-fetch the proposal, and drop the id if the user cannot access it.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from api.client import ApiError, ProposalApiClient

DEFAULTS: dict[str, Any] = {
    "active_proposal": None,
    "show_details": True,
    "flash": None,
    "restored": False,
}


def init_session(session: MutableMapping[str, Any]) -> None:
    for key, value in DEFAULTS.items():
        session.setdefault(key, value)


def set_active(session: MutableMapping[str, Any], query: MutableMapping[str, Any], proposal_id: str | None) -> None:
    session["active_proposal"] = proposal_id
    if proposal_id:
        query["proposal"] = proposal_id
    elif "proposal" in query:
        del query["proposal"]


def restore_session(session: MutableMapping[str, Any], query: MutableMapping[str, Any], client: ProposalApiClient) -> str | None:
    """Restore the active proposal from the URL once per session. Returns a warning, if any."""
    if session.get("restored"):
        return None
    session["restored"] = True
    pid = query.get("proposal")
    if not pid or session.get("active_proposal"):
        return None
    try:
        client.get_proposal(pid)
    except ApiError as exc:
        if exc.status in (403, 404):
            set_active(session, query, None)
            return "That proposal could not be found or you don't have access to it."
        session["restored"] = False  # transient failure: keep the URL and try again on next rerun
        return f"Could not restore the proposal yet: {exc}"
    session["active_proposal"] = pid
    return None
