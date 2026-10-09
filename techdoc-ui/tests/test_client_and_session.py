"""API client error handling, response validation, session restoration and stepper logic."""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import SecretStr

from api.client import ApiError, ProposalApiClient
from api.schemas import ProposalSummary
from components.workflow_status import step_states
from config import FrontendSettings
from state import init_session, restore_session, set_active

SUMMARY = {
    "proposal_id": "PRP-1", "title": "T", "customer_name": "C", "workflow_status": "awaiting_approval",
    "current_stage": "financial_estimation", "run_state": "idle", "last_error": None, "pending_questions": [],
    "awaiting": "approval", "approval_status": "pending", "revision_number": 0,
    "artifact_versions": {"requirements": 1, "technical_proposal": 1, "financial_estimate": 1, "document": None},
    "stale_artifacts": [], "estimate": {"version": 1, "currency": "USD", "total_cost": "100.00", "total_hours": "10",
                                        "estimated_duration": "8 weeks", "status": "ready_for_approval", "approval_status": "pending"},
    "has_document": False, "recent_errors": [], "created_at": "2026-10-08T10:00:00Z", "updated_at": "2026-10-08T10:00:00Z",
}


def make_client(handler, **kw) -> ProposalApiClient:  # type: ignore[no-untyped-def]
    s = FrontendSettings(api_base_url="http://api.test", poll_interval_seconds=0, poll_timeout_seconds=5, **kw)
    return ProposalApiClient(s, transport=httpx.MockTransport(handler))


def test_sends_identity_and_idempotency_headers():
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(202, json=SUMMARY)

    make_client(handler, user_id="alice").send_message("PRP-1", "hi")
    assert seen[0].headers["x-user-id"] == "alice" and seen[0].headers["idempotency-key"]
    assert json.loads(seen[0].content) == {"content": "hi"}
    make_client(handler, auth_mode="api_key", api_key=SecretStr("k1")).get_proposal("PRP-1")
    assert seen[1].headers["authorization"] == "Bearer k1"


def test_backend_error_envelope_is_surfaced():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"error": {"code": "conflict", "message": "Estimate v1 is stale", "trace_id": "abc"}})

    with pytest.raises(ApiError) as e:
        make_client(handler).decide("PRP-1", "approve", 1)
    assert e.value.status == 409 and "stale" in e.value.message and e.value.trace_id == "abc" and e.value.retryable
    assert "ref abc" in str(e.value)


def test_validation_and_server_errors_are_friendly():
    def h422(req: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"error": {"code": "validation_error", "message": "bad", "trace_id": "t",
                                                   "details": [{"loc": ["body", "title"], "msg": "short"}]}})

    with pytest.raises(ApiError) as e:
        make_client(h422).create_proposal("", "", "")
    assert e.value.status == 422 and not e.value.retryable

    def h500(req: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="<html>boom</html>")

    with pytest.raises(ApiError) as e:
        make_client(h500).get_proposal("x")
    assert e.value.retryable and "unexpected error" in e.value.message


def test_network_failures_and_timeouts():
    def down(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=req)

    with pytest.raises(ApiError) as e:
        make_client(down).list_proposals()
    assert e.value.code == "unreachable" and e.value.retryable

    def slow(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=req)

    with pytest.raises(ApiError) as e:
        make_client(slow).health()
    assert e.value.code == "timeout"


def test_unexpected_payload_rejected_and_missing_artifact_is_none():
    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/estimate"):
            return httpx.Response(404, json={"error": {"code": "not_found", "message": "No estimate", "trace_id": "t"}})
        return httpx.Response(200, json={"unexpected": True})

    c = make_client(handler)
    assert c.artifact("PRP-1", "estimate") is None
    with pytest.raises(ApiError) as e:
        c.get_proposal("PRP-1")
    assert e.value.code == "bad_response"


def test_wait_until_idle_polls():
    states = iter([{**SUMMARY, "run_state": "running"}, {**SUMMARY, "run_state": "running"}, SUMMARY])

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=next(states))

    ticks = []
    s = make_client(handler).wait_until_idle("PRP-1", on_tick=ticks.append, sleep=lambda _: None)
    assert s.run_state == "idle" and len(ticks) == 2


def test_document_download_filename():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.params.get("version") == "2"
        return httpx.Response(200, content=b"PK..", headers={"content-disposition": 'attachment; filename="proposal_PRP-1_v2.docx"'})

    data, name = make_client(handler).download_document("PRP-1", 2)
    assert data == b"PK.." and name == "proposal_PRP-1_v2.docx"


# ---- session restore -----------------------------------------------------------------------


def test_session_restored_from_url_after_refresh():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SUMMARY)

    session, query = {}, {"proposal": "PRP-1"}
    init_session(session)
    assert restore_session(session, query, make_client(handler)) is None
    assert session["active_proposal"] == "PRP-1"
    assert restore_session(session, query, make_client(handler)) is None  # only once


def test_restore_drops_inaccessible_proposal():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"code": "not_found", "message": "Proposal not found", "trace_id": "t"}})

    session, query = {}, {"proposal": "PRP-OTHER"}
    init_session(session)
    msg = restore_session(session, query, make_client(handler))
    assert msg and session["active_proposal"] is None and "proposal" not in query


def test_restore_keeps_url_on_transient_failure():
    def handler(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=req)

    session, query = {}, {"proposal": "PRP-1"}
    init_session(session)
    assert restore_session(session, query, make_client(handler))
    assert query["proposal"] == "PRP-1" and session["restored"] is False


def test_set_active_syncs_query():
    session, query = {}, {}
    set_active(session, query, "PRP-9")
    assert query == {"proposal": "PRP-9"}
    set_active(session, query, None)
    assert query == {}


# ---- stepper -------------------------------------------------------------------------------


def test_step_states():
    s = ProposalSummary.model_validate({**SUMMARY, "current_stage": "approval"})
    labels = step_states(s)
    assert [c for _, c, _ in labels][:3] == ["done", "done", "done"]
    assert labels[3][1] == "blocked" and labels[3][2] == "Your decision"
    done = ProposalSummary.model_validate({**SUMMARY, "workflow_status": "completed", "current_stage": "completed", "awaiting": None,
                                           "approval_status": "approved", "has_document": True,
                                           "artifact_versions": {**SUMMARY["artifact_versions"], "document": 1}})
    assert all(c == "done" for _, c, _ in step_states(done))
    stale = ProposalSummary.model_validate({**SUMMARY, "current_stage": "approval", "stale_artifacts": ["technical_proposal"]})
    assert "stale" in step_states(stale)[1][1]
