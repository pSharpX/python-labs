import asyncio
import uuid

from src.configs.database_config import async_session_maker, async_engine
from src.repositories.sqlalchemy_proposal_repository import SQLAlchemyProposalRepository
from settings import ApplicationSettings, DocumentSettings
from src.agents.requirements_scout_agent import RequirementsValidator
from src.services.document_service import DocumentService
from src.services.financial_service import FinancialService, FileRateProvider, load_financial_rules
from src.services.version_service import VersionService
from src import TechDocBuilderGraph, WorkflowSnapshot
from src.shared import UserResponse, UserAction
from src.tools.mcp import MCPToolsAdapter, MCPSettings


def _ask(snap: WorkflowSnapshot) -> UserResponse:
    payload = snap.interrupt or {}
    print(payload)

    interrupt_type = payload["type"]
    if interrupt_type == "requirements_clarification":
        print("\nSe necesita mayor información para continuar con el analisis:")
        questions = payload["questions"]
        for idx, q in enumerate(questions):
            print(f"{idx+1}. {q["question"]}")
        answers = input("\nRespuesta: ")
        return UserResponse(action=UserAction.PROVIDE_INFORMATION, information=answers)

    if interrupt_type == "financial_approval":
        print("\n" + payload["financial_proposal"])
        while True:
            choice = input("\n[a]pprove / request [c]hanges to the estimate / change [r]equirements: ").strip().lower()
            if choice == "a":
                return UserResponse(action=UserAction.APPROVE)
            if choice == "c":
                return UserResponse(action=UserAction.REQUEST_CHANGES, feedback=input("Feedback: "))
            if choice == "r":
                return UserResponse(action=UserAction.CHANGE_REQUIREMENTS, changes=input("Requirement change: "))
    raise ValueError("Invalid interrupt type")

async def run_agent():
    mcp_settings = MCPSettings()
    app_settings = ApplicationSettings()
    document_settings = DocumentSettings()

    mcp_adapter = await MCPToolsAdapter.acreate(mcp_settings)
    proposal_repository = SQLAlchemyProposalRepository(
        session_maker=async_session_maker,
        engine=async_engine
    ),

    workflow = TechDocBuilderGraph(
        mcp_adapter=mcp_adapter,
        version_service=VersionService(repo=proposal_repository),
        validator=RequirementsValidator.from_file(app_settings.validation_rules_file),
        proposal_repository=proposal_repository,
        financial_service=FinancialService(
            rate_provider=FileRateProvider(app_settings.rate_card_file),
            rules=load_financial_rules(app_settings.rules_file)
        ),
        document_service=DocumentService(document_settings, app_settings.documents_output_dir),
    )
    workflow.draw_workflow()

    print("Welcome to TechDoc Builder Workflow, your helpful assistant!")
    print("Start typing ('c' for exit) >> ")

    request: str = input()
    proposal_id = str(uuid.uuid4())
    snap = await workflow.start(proposal_id, request)

    while snap.waiting_for_user:
        response: UserResponse = _ask(snap)
        snap = await workflow.resume(proposal_id, response)

    print(f"\nFinal status: {snap.status if snap.status else None}")
    if snap.values.get("errors"):
        print("Errors:", *snap.values["errors"], sep="\n  ")


if __name__ == '__main__':
    # run_agent()
    asyncio.run(run_agent())
