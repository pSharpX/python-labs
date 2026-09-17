from operator import add
from typing import Literal, Annotated

from langchain.agents import AgentState
from pydantic import Field, BaseModel

from constants import Priority
from reducers import replace_string, merge_status


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
    context: Annotated[str, replace_string]
    problem_need: Annotated[str, replace_string]

    objectives: Annotated[list[str], add]
    expected_results: Annotated[list[str], add]

    actors: Annotated[list[Actor], add]
    processes: Annotated[list[Process], add]

    functional_requirements: Annotated[list[Requirement], add]
    non_functional_requirements: Annotated[list[
        NonFunctionalRequirement
    ], add]

    business_rules: Annotated[list[str], add]
    integrations: Annotated[list[Integration], add]

    data_and_volumetrics: Annotated[list[str], add]

    scope: ProposalScope

    dependencies: Annotated[list[str], add]
    constraints: Annotated[list[str], add]

    risks: Annotated[list[Risk], add]
    assumptions: Annotated[list[Assumption], add]

    missing_information: Annotated[list[
        MissingInformation
    ], add]
    client_questions: Annotated[list[ClientQuestion], add]

    # Current interaction status
    waiting_for_customer: bool
    status: Annotated[str, merge_status]

    # Generated output
    final_brief: str | None

class TechDocBuilderInput(TechDocReqScoutState):
    pass
    # user_request: str = Field(
    #     description="Solicitud del usuario que contiene los requerimientos funcionales y el objetivo del documento a elaborar.",
    # )
    # resources: Optional[list[str]] = Field(
    #     description="Lista de recursos adicionales que contienen requerimientos, contexto o fuentes de información relevantes para elaborar el documento.",
    # )

class TechDocBuilderOutput(BaseModel):
    raw_document_content: str = Field(
        description="Contenido completo del documento generado en formato Markdown, listo para su procesamiento o almacenamiento.",
    )
    final_document: str = Field(
        description="Versión final del documento técnico, estructurada y preparada para ser presentada al usuario.",
    )

class TechDocBuilderState(TechDocReqScoutState):
    requirements: str
    technical_document: str
    financial_document: str
