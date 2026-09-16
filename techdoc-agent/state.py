from typing import Literal

from langchain.agents import AgentState
from pydantic import Field, BaseModel

Priority = Literal["must", "should", "could", "to_be_defined"]
Criticality = Literal["Critical", "Important", "Desirable"]
Status = Literal["analyzing", "awaiting_client_information", "ready_for_architecture"]

class Requirement(BaseModel):
    id: str
    description: str
    priority: Priority = "to_be_defined"

    actor: str | None = None
    process: str | None = None

    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)

    source: str | None = None
    confirmed: bool = False

class NonFunctionalRequirement(BaseModel):
    id: str
    category: str
    description: str
    priority: Priority = "to_be_defined"

    acceptance_criteria: list[str] = Field(default_factory=list)

    source: str | None = None
    confirmed: bool = False

class Actor(BaseModel):
    name: str
    type: str
    responsibility: str
    source: str | None = None

class Process(BaseModel):
    name: str
    objective: str
    actors: list[str] = Field(default_factory=list)

    main_flow: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    result: str | None = None

class Integration(BaseModel):
    system: str
    purpose: str
    data: list[str] = Field(default_factory=list)

    direction: str | None = None
    frequency: str | None = None
    status: str = "por confirmar"

class Risk(BaseModel):
    description: str
    impact: str
    cause: str
    action_validation: str

class Assumption(BaseModel):
    description: str
    requires_validation: bool = True
    source: str | None = None

class MissingInformation(BaseModel):
    description: str
    criticality: Literal[
        "critical",
        "important",
        "desirable",
    ]
    reason: str | None

class ClientQuestion(BaseModel):
    question: str
    reason: str
    related_to: str | None = None

class ProposalScope(BaseModel):
    included: list[str] = Field(default_factory=list)
    excluded: list[str] = Field(default_factory=list)
    to_confirm: list[str] = Field(default_factory=list)

class TechDocReqScoutState(AgentState):
    user_request: str
    resources: list[str]
    # Canonical functional analysis
    context: str | None
    problem_need: str | None

    objectives: list[str]
    expected_results: list[str]

    actors: list[Actor]
    processes: list[Process]

    functional_requirements: list[Requirement]

    non_functional_requirements: list[
        NonFunctionalRequirement
    ]

    business_rules: list[str]

    integrations: list[Integration]

    data_and_volumetrics: list[str]

    scope: ProposalScope

    dependencies: list[str]
    constraints: list[str]

    risks: list[Risk]
    assumptions: list[Assumption]

    missing_information: list[MissingInformation]

    client_questions: list[ClientQuestion]

    # Current interaction status
    waiting_for_customer: bool
    status: Status

    # Generated output
    final_brief: str | None