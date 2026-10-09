"""HTTP client for the Proposal Studio API.

Encapsulates base URL, auth headers, timeouts, idempotency keys, error mapping and
response validation. UI code never calls httpx directly.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any

import httpx
from pydantic import ValidationError

from api.schemas import Message, ProposalListItem, ProposalSummary, Versions
from config import FrontendSettings


class ApiError(Exception):
    """User-presentable API failure."""

    def __init__(self, message: str, *, status: int | None = None, code: str = "error",
                 trace_id: str | None = None, retryable: bool = False) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.trace_id = trace_id
        self.retryable = retryable

    def __str__(self) -> str:
        suffix = f" (ref {self.trace_id})" if self.trace_id else ""
        return f"{self.message}{suffix}"


_FRIENDLY = {
    401: "You are not signed in or your credentials are invalid.",
    403: "You don't have access to this proposal.",
    404: "Not found.",
    409: None,  # backend message is already user-friendly
    422: "Some input was invalid.",
}


class ProposalApiClient:
    def __init__(self, settings: FrontendSettings, transport: httpx.BaseTransport | None = None) -> None:
        headers = {"Accept": "application/json"}
        if settings.auth_mode == "api_key" and settings.api_key:
            headers["Authorization"] = f"Bearer {settings.api_key.get_secret_value()}"
        else:
            headers["X-User-Id"] = settings.user_id
        self._s = settings
        self._http = httpx.Client(base_url=settings.api_base_url.rstrip("/"), headers=headers,
                                  timeout=settings.api_timeout_seconds, transport=transport)

    # ---- core ------------------------------------------------------------------------
    def _request(self, method: str, path: str, *, json: Any = None, params: dict[str, Any] | None = None,
                 idempotent: bool = False) -> httpx.Response:
        headers = {"Idempotency-Key": uuid.uuid4().hex} if idempotent else None
        try:
            resp = self._http.request(method, path, json=json, params=params, headers=headers)
        except httpx.TimeoutException as exc:
            raise ApiError("The server took too long to respond. Please retry.", code="timeout", retryable=True) from exc
        except httpx.TransportError as exc:
            raise ApiError(f"Cannot reach the proposal service at {self._s.api_base_url}.", code="unreachable",
                           retryable=True) from exc
        if resp.status_code >= 400:
            raise self._to_error(resp)
        return resp

    @staticmethod
    def _to_error(resp: httpx.Response) -> ApiError:
        code, message, trace = "http_error", "", resp.headers.get("x-trace-id")
        try:
            err = resp.json().get("error", {})
            code, message, trace = err.get("code", code), err.get("message", ""), err.get("trace_id", trace)
            if err.get("details"):
                fields = ", ".join(".".join(str(x) for x in d.get("loc", [])[1:]) for d in err["details"])
                message = f"{message}: {fields}" if fields else message
        except (ValueError, AttributeError):
            pass
        friendly = _FRIENDLY.get(resp.status_code)
        if resp.status_code >= 500:
            friendly = "The proposal service hit an unexpected error. Please retry."
        return ApiError(friendly or message or f"Request failed ({resp.status_code})", status=resp.status_code,
                        code=code, trace_id=trace, retryable=resp.status_code >= 500 or resp.status_code == 409)

    @staticmethod
    def _parse(model: Any, data: Any) -> Any:
        try:
            return model.model_validate(data)
        except ValidationError as exc:
            raise ApiError("Received an unexpected response from the server.", code="bad_response") from exc

    # ---- endpoints -------------------------------------------------------------------
    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health").json()

    def list_proposals(self) -> list[ProposalListItem]:
        return [self._parse(ProposalListItem, x) for x in self._request("GET", "/api/v1/proposals").json()]

    def create_proposal(self, title: str, customer: str, message: str) -> ProposalSummary:
        r = self._request("POST", "/api/v1/proposals", json={"title": title, "customer_name": customer, "message": message},
                          idempotent=True)
        return self._parse(ProposalSummary, r.json())

    def get_proposal(self, proposal_id: str) -> ProposalSummary:
        return self._parse(ProposalSummary, self._request("GET", f"/api/v1/proposals/{proposal_id}").json())

    def send_message(self, proposal_id: str, content: str) -> ProposalSummary:
        r = self._request("POST", f"/api/v1/proposals/{proposal_id}/messages", json={"content": content}, idempotent=True)
        return self._parse(ProposalSummary, r.json())

    def messages(self, proposal_id: str) -> list[Message]:
        return [self._parse(Message, m) for m in self._request("GET", f"/api/v1/proposals/{proposal_id}/messages").json()]

    def artifact(self, proposal_id: str, kind: str) -> dict[str, Any] | None:
        """kind: requirements | technical-proposal | estimate. Returns None when not produced yet."""
        try:
            return self._request("GET", f"/api/v1/proposals/{proposal_id}/{kind}").json()
        except ApiError as exc:
            if exc.status == 404:
                return None
            raise

    def decide(self, proposal_id: str, decision: str, estimate_version: int, feedback: str | None = None) -> ProposalSummary:
        body = {"decision": decision, "estimate_version": estimate_version, "feedback": feedback or None}
        r = self._request("POST", f"/api/v1/proposals/{proposal_id}/approval", json=body, idempotent=True)
        return self._parse(ProposalSummary, r.json())

    def resume(self, proposal_id: str, action: str = "retry") -> ProposalSummary:
        r = self._request("POST", f"/api/v1/proposals/{proposal_id}/resume", json={"action": action})
        return self._parse(ProposalSummary, r.json())

    def versions(self, proposal_id: str) -> Versions:
        return self._parse(Versions, self._request("GET", f"/api/v1/proposals/{proposal_id}/versions").json())

    def download_document(self, proposal_id: str, version: int | None = None) -> tuple[bytes, str]:
        params = {"version": version} if version else None
        r = self._request("GET", f"/api/v1/proposals/{proposal_id}/document", params=params)
        disposition = r.headers.get("content-disposition", "")
        filename = disposition.split("filename=")[-1].strip('"') if "filename=" in disposition else f"{proposal_id}.docx"
        return r.content, filename

    def wait_until_idle(self, proposal_id: str, on_tick: Callable[[ProposalSummary], None] | None = None,
                        sleep: Callable[[float], None] = time.sleep) -> ProposalSummary:
        """Poll until the background run finishes or the poll timeout elapses."""
        deadline = time.monotonic() + self._s.poll_timeout_seconds
        summary = self.get_proposal(proposal_id)
        while summary.is_running and time.monotonic() < deadline:
            if on_tick:
                on_tick(summary)
            sleep(self._s.poll_interval_seconds)
            summary = self.get_proposal(proposal_id)
        return summary
