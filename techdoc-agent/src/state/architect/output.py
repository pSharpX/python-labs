from pydantic import BaseModel, ConfigDict, Field

from src.shared import ArchitectureComponent, TechnologyDecision, TechnicalIntegration, ScalabilityDesign, SecurityDesign, \
    AvailabilityDesign, ObservabilityDesign, DeploymentDesign, DataArchitecture, DocumentationSource


class TechArchitectOutputSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    solution_overview: str
    architecture_components: list[ArchitectureComponent] = Field(default_factory=list)
    technology_decisions: list[TechnologyDecision] = Field(default_factory=list)
    integrations: list[TechnicalIntegration] = Field(default_factory=list)
    security: SecurityDesign | None = None
    scalability: ScalabilityDesign | None = None
    availability: AvailabilityDesign | None = None
    observability: ObservabilityDesign | None = None
    deployment: DeploymentDesign | None = None
    data_architecture: DataArchitecture | None = None
    implementation_approach: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    technical_risks: list[str] = Field(default_factory=list)
    documentation_sources: list[DocumentationSource] = Field(default_factory=list)
    technical_proposal: str