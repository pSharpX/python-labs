from typing import TypedDict

from src.shared import ArchitectureComponent, TechnologyDecision, TechnicalIntegration, SecurityDesign, ScalabilityDesign, \
    ObservabilityDesign, AvailabilityDesign, DeploymentDesign, DataArchitecture, DocumentationSource


class TechArchitectAgentState(TypedDict):
    requirements_version: int
    architecture: object | None
    solution_overview: str | None
    architecture_components: list[ArchitectureComponent]
    technology_decisions: list[TechnologyDecision]
    integrations: list[TechnicalIntegration]
    security: SecurityDesign | None
    scalability: ScalabilityDesign | None
    availability: AvailabilityDesign | None
    observability: ObservabilityDesign | None
    deployment: DeploymentDesign | None
    data_architecture: DataArchitecture | None
    implementation_approach: list[str]
    assumptions: list[str]
    technical_risks: list[str]
    documentation_sources: list[DocumentationSource]
    technical_proposal: str
    status: str
    version: int
    stale: bool