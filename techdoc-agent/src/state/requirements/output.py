from pydantic import BaseModel, ConfigDict, Field

from src.shared import (Actor, Process, Integration, ProposalScope, MissingInformation,
                        NonFunctionalRequirement, Requirement)


class RequirementsOutputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_statement: str | None = None
    business_objectives: list[str] = Field(default_factory=list)

    expected_results: list[str] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    business_processes: list[Process] = Field(default_factory=list)

    functional_requirements: list[Requirement] = Field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(default_factory=list)

    business_rules: list[str] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)

    data_and_volumetrics: list[str] = Field(default_factory=list)
    scope: ProposalScope | None = None

    assumptions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    missing_information: list[MissingInformation] = Field(default_factory=list)
    client_questions: list[str] = Field(default_factory=list)
    ready_for_architecture: bool = False

    readiness_reason: str = ""