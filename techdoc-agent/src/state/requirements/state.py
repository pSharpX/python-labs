from typing import TypedDict

from src.shared import (Process, Actor, Requirement, NonFunctionalRequirement, Integration,
                        ProposalScope, Risk, Assumption, MissingInformation, ClientQuestion)


class RequirementsAgentState(TypedDict):
    raw_requirements: str
    # Canonical functional analysis
    context: str
    problem_need: str

    objectives: list[str]
    expected_results: list[str]

    actors: list[Actor]
    processes: list[Process]

    functional_requirements: list[Requirement]
    non_functional_requirements: list[NonFunctionalRequirement]

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

    ready_for_architecture: bool
    status: str
    version: int