from __future__ import annotations
from typing import Literal
from src.state import WorkflowState


def route_after_requirements(state: WorkflowState) -> Literal["technical_architect", "awaiting_requirements", "failed"]:
    if state.get("status") == "error":
        return "failed"
    req = state.get("requirements")
    return "technical_architect" if req and req.get("ready_for_architecture", False) else "awaiting_requirements"


def route_after_technical(state: WorkflowState) -> Literal["financial_estimator", "failed"]:
    return "failed" if state.get("status") == "error" else "financial_estimator"


def route_after_financial(state: WorkflowState) -> Literal["request_financial_approval", "failed"]:
    return "failed" if state.get("status") == "error" else "request_financial_approval"


def route_after_approval(state: WorkflowState) -> Literal["complete", "financial_estimator"]:
    financial = state.get("financial_estimation") or {}
    return "complete" if financial.get("approval_status") == "approved" else "financial_estimator"


def route_after_revision_check(state: WorkflowState) -> Literal["requirements_agent", "requirements_agent"]:
    return "requirements_agent"
