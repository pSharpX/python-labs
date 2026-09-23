from typing import Annotated

from langchain.agents import AgentState

from src.shared import replace_string, merge_strings
from state import Process, Actor, Requirement, NonFunctionalRequirement, Integration, ProposalScope, Risk, Assumption, \
    MissingInformation, ClientQuestion
from .reducers import merge_status, merge_actors, merge_processes, merge_requirements, \
    merge_non_functional_requirements, merge_integrations, merge_risks, merge_assumptions, merge_missing_information, \
    merge_client_questions


class RequirementsState(AgentState):
    user_request: str
    resources: list[str]
    # Canonical functional analysis
    context: Annotated[str, replace_string]
    problem_need: Annotated[str, replace_string]

    objectives: Annotated[list[str], merge_strings]
    expected_results: Annotated[list[str], merge_strings]

    actors: Annotated[list[Actor], merge_actors]
    processes: Annotated[list[Process], merge_processes]

    functional_requirements: Annotated[list[Requirement], merge_requirements]
    non_functional_requirements: Annotated[list[
        NonFunctionalRequirement
    ], merge_non_functional_requirements]

    business_rules: Annotated[list[str], merge_strings]
    integrations: Annotated[list[Integration], merge_integrations]

    data_and_volumetrics: Annotated[list[str], merge_strings]
    scope: ProposalScope

    dependencies: Annotated[list[str], merge_strings]
    constraints: Annotated[list[str], merge_strings]

    risks: Annotated[list[Risk], merge_risks]
    assumptions: Annotated[list[Assumption], merge_assumptions]

    missing_information: Annotated[list[
        MissingInformation
    ], merge_missing_information]
    client_questions: Annotated[list[ClientQuestion], merge_client_questions]

    status: Annotated[str, merge_status]