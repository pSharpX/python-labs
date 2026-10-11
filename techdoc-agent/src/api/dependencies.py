"""Dependency wiring (composition root) and authentication hooks."""

from __future__ import annotations

from contextlib import AsyncExitStack
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request, status

from src.agents.requirements_scout_agent import RequirementsValidator
from src.configs.database_config import async_session_maker, async_engine
from src.repositories.sqlalchemy_proposal_repository import SQLAlchemyProposalRepository
from settings import ApplicationSettings, DocumentSettings
from src import TechDocBuilderGraph
from src.services.document_service import DocumentService
from src.services.financial_service import FileRateProvider, FinancialService, RateProvider, load_financial_rules
from src.services.proposal_service import Principal, ProposalService
from src.services.version_service import VersionService
from src.tools.mcp import MCPSettings, MCPToolsAdapter


@dataclass
class AppContainer:
    settings: ApplicationSettings
    repository: SQLAlchemyProposalRepository
    documents: DocumentService
    proposals: ProposalService

    async def aclose(self) -> None:
        await self.proposals.drain()

async def build_container(
        settings: ApplicationSettings,
) -> AppContainer:
    """Build every component from settings. Overrides exist for tests and integrations."""
    proposal_repository = SQLAlchemyProposalRepository(
        session_maker=async_session_maker,
        engine=async_engine
    )

    await proposal_repository.init()
    await proposal_repository.reset_stale_runs()

    mcp_settings = MCPSettings()
    app_settings = ApplicationSettings()
    document_settings = DocumentSettings()

    mcp_adapter = await MCPToolsAdapter.acreate(mcp_settings)
    document_service = DocumentService(document_settings, app_settings.documents_output_dir)

    workflow = TechDocBuilderGraph(
        mcp_adapter=mcp_adapter,
        version_service=VersionService(repo=proposal_repository),
        validator=RequirementsValidator.from_file(app_settings.validation_rules_file),
        proposal_repository=proposal_repository,
        financial_service=FinancialService(
            rate_provider=FileRateProvider(app_settings.rate_card_file),
            rules=load_financial_rules(app_settings.rules_file)
        ),
        document_service=document_service,
    )
    graph = workflow.get_compiled_state_graph()
    proposal_service = ProposalService(graph=graph, repo=proposal_repository)

    return AppContainer(settings, proposal_repository, document_service, proposal_service)


# ---- request-scoped dependencies -----------------------------------------------------


def get_container(request: Request) -> AppContainer:
    return request.app.state.container  # type: ignore[no-any-return]


def get_service(container: AppContainer = Depends(get_container)) -> ProposalService:
    return container.proposals


async def get_principal(
        container: AppContainer = Depends(get_container),
        authorization: str | None = Header(default=None),
        x_user_id: str | None = Header(default=None),
) -> Principal:
    """Authentication hook.

    * ``dev`` mode: identity from ``X-User-Id`` (or the configured default user).
    * ``api_key`` mode: ``Authorization: Bearer <key>`` mapped to a user id.
    Replace this function to integrate OIDC/JWT; the rest of the API only needs a Principal.
    """
    auth = container.settings.auth
    if auth.mode == "dev":
        user = (x_user_id or auth.dev_default_user).strip()[:128]
        return Principal(user_id=user, is_admin=user in auth.admin_users)
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token",
                            headers={"WWW-Authenticate": "Bearer"})
    user_id = auth.api_keys.get(authorization[7:].strip())
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    return Principal(user_id=user_id, is_admin=user_id in auth.admin_users)
