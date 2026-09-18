from typing import Annotated

from langchain.agents import AgentState

from models import Process, Actor, Requirement, NonFunctionalRequirement, Integration, ProposalScope, Risk, Assumption, \
    MissingInformation, ClientQuestion, Requirements
from reducers import replace_string, merge_status, merge_strings, merge_actors, merge_processes, merge_requirements, \
    merge_non_functional_requirements, merge_integrations, merge_risks, merge_assumptions, merge_missing_information, \
    merge_client_questions


class TechDocReqScoutState(AgentState):
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

    # Current interaction status
    waiting_for_customer: bool
    status: Annotated[str, merge_status]

    requirements: Requirements

    # Generated output
    final_brief: str | None

# class TechDocBuilderInput(TechDocReqScoutState):
#     user_request: str = Field(
#         description="Solicitud del usuario que contiene los requerimientos funcionales y el objetivo del documento a elaborar.",
#     )
#     resources: Optional[list[str]] = Field(
#         description="Lista de recursos adicionales que contienen requerimientos, contexto o fuentes de información relevantes para elaborar el documento.",
#     )
#
# class TechDocBuilderOutput(BaseModel):
#     raw_document_content: str = Field(
#         description="Contenido completo del documento generado en formato Markdown, listo para su procesamiento o almacenamiento.",
#     )
#     final_document: str = Field(
#         description="Versión final del documento técnico, estructurada y preparada para ser presentada al usuario.",
#     )

class TechDocBuilderState(TechDocReqScoutState):
    technical_document: str
    financial_document: str
