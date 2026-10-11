from typing import Any

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from src.domain.proposal_record import ProposalRecord, RunState
from src.domain.stored_artifact import StoredArtifact
from src.domain.stored_message import StoredMessage
from src.mappers.artifact_mapper import ArtifactMapper
from src.mappers.message_mapper import MessageMapper
from src.mappers.proposal_mapper import ProposalMapper
from src.models.approval import ApprovalModel
from src.models.artifact import ArtifactModel
from src.models.base import Base
from src.models.document import DocumentModel
from src.models.idempotency import IdempotencyModel
from src.models.message import MessageModel
from src.models.proposal import ProposalModel
from src.shared.enums import ArtifactType
from src.shared.models import ApprovalRecord, DocumentMetadata
from src.utils.hashing import utcnow


class SQLAlchemyProposalRepository:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession], engine: AsyncEngine) -> None:
        self._session_maker = session_maker
        self._engine = engine

    async def init(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # ---- proposals -------------------------------------------------------------------
    async def create_proposal(self, record: ProposalRecord) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                orm_model = ProposalMapper.to_orm(record)
                session.add(orm_model)

    async def get_proposal(self, proposal_id: str) -> ProposalRecord | None:
        async with self._session_maker() as session:
            model = await session.get(ProposalModel, proposal_id)
            if not model:
                return None
            return ProposalMapper.to_dto(model)

    async def list_proposals(self, owner_id: str | None) -> list[ProposalRecord]:
        async with self._session_maker() as session:
            stmt = select(ProposalModel).order_by(ProposalModel.updated_at.desc())
            if owner_id is not None:
                stmt = stmt.where(ProposalModel.owner_id == owner_id)
            result = await session.execute(stmt)
            return [ProposalMapper.to_dto(m) for m in result.scalars().all()]

    async def update_proposal(self, proposal_id: str, **fields: Any) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                model = await session.get(ProposalModel, proposal_id)
                if not model:
                    raise KeyError(proposal_id)

                rec = ProposalMapper.to_dto(model)
                data = rec.model_dump()
                data.update({k: v for k, v in fields.items() if k != "run_state"})
                data["updated_at"] = utcnow()

                updated_rec = ProposalRecord.model_validate(data)
                model.data = updated_rec.model_dump(mode="json")
                model.updated_at = updated_rec.updated_at

    async def try_start_run(self, proposal_id: str) -> bool:
        async with self._session_maker() as session:
            async with session.begin():
                stmt = (
                    update(ProposalModel)
                    .where(ProposalModel.proposal_id == proposal_id, ProposalModel.run_state != RunState.RUNNING)
                    .values(run_state=RunState.RUNNING, updated_at=utcnow())
                )
                result = await session.execute(stmt)
                return result.rowcount == 1

    async def finish_run(self, proposal_id: str, run_state: str, error: str | None = None) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                stmt = (
                    update(ProposalModel)
                    .where(ProposalModel.proposal_id == proposal_id)
                    .values(run_state=run_state, updated_at=utcnow())
                )
                await session.execute(stmt)
        await self.update_proposal(proposal_id, last_error=error)

    async def reset_stale_runs(self) -> int:
        async with self._session_maker() as session:
            async with session.begin():
                stmt = (
                    update(ProposalModel)
                    .where(ProposalModel.run_state == RunState.RUNNING)
                    .values(run_state=RunState.FAILED)
                )
                result = await session.execute(stmt)
                return result.rowcount

    # ---- messages --------------------------------------------------------------------
    async def add_message(self, proposal_id: str, role: str, content: str, kind: str = "chat") -> None:
        async with self._session_maker() as session:
            async with session.begin():
                msg = MessageModel(
                    proposal_id=proposal_id,
                    role=role,
                    content=content,
                    kind=kind,
                    created_at=utcnow(),
                )
                session.add(msg)

    async def list_messages(self, proposal_id: str) -> list[StoredMessage]:
        async with self._session_maker() as session:
            stmt = select(MessageModel).where(MessageModel.proposal_id == proposal_id).order_by(MessageModel.id)
            result = await session.execute(stmt)
            return [MessageMapper.to_dto(m) for m in result.scalars().all()]

    # ---- artifacts -------------------------------------------------------------------
    async def save_artifact(self, artifact: StoredArtifact) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                orm_model = ArtifactMapper.to_orm(artifact)
                await session.merge(orm_model)

    async def latest_artifact(self, proposal_id: str, artifact_type: ArtifactType) -> StoredArtifact | None:
        async with self._session_maker() as session:
            stmt = (
                select(ArtifactModel)
                .where(ArtifactModel.proposal_id == proposal_id, ArtifactModel.artifact_type == artifact_type.value)
                .order_by(ArtifactModel.version.desc())
                .limit(1)
            )
            model = (await session.execute(stmt)).scalars().first()
            return ArtifactMapper.to_dto(model) if model else None

    async def get_artifact(self, proposal_id: str, artifact_type: ArtifactType, version: int) -> StoredArtifact | None:
        async with self._session_maker() as session:
            stmt = select(ArtifactModel).where(
                ArtifactModel.proposal_id == proposal_id,
                ArtifactModel.artifact_type == artifact_type.value,
                ArtifactModel.version == version,
            )
            model = (await session.execute(stmt)).scalars().first()
            return ArtifactMapper.to_dto(model) if model else None

    async def list_artifacts(self, proposal_id: str) -> list[StoredArtifact]:
        async with self._session_maker() as session:
            stmt = (
                select(ArtifactModel)
                .where(ArtifactModel.proposal_id == proposal_id)
                .order_by(ArtifactModel.artifact_type, ArtifactModel.version)
            )
            result = await session.execute(stmt)
            return [ArtifactMapper.to_dto(m) for m in result.scalars().all()]

    async def next_version(self, proposal_id: str, artifact_type: ArtifactType) -> int:
        async with self._session_maker() as session:
            stmt = select(func.coalesce(func.max(ArtifactModel.version), 0)).where(
                ArtifactModel.proposal_id == proposal_id,
                ArtifactModel.artifact_type == artifact_type.value,
            )
            max_v = (await session.execute(stmt)).scalar_one()
            return int(max_v) + 1

    # ---- approvals -------------------------------------------------------------------
    async def save_approval(self, proposal_id: str, record: ApprovalRecord) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                approval = ApprovalModel(
                    proposal_id=proposal_id,
                    data=record.model_dump(mode="json"),
                    created_at=record.decided_at,
                )
                session.add(approval)

    async def list_approvals(self, proposal_id: str) -> list[ApprovalRecord]:
        async with self._session_maker() as session:
            stmt = select(ApprovalModel).where(ApprovalModel.proposal_id == proposal_id).order_by(ApprovalModel.id)
            result = await session.execute(stmt)
            return [ApprovalRecord.model_validate(m.data) for m in result.scalars().all()]

    # ---- documents -------------------------------------------------------------------
    async def save_document(self, meta: DocumentMetadata) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                doc = DocumentModel(
                    proposal_id=meta.proposal_id,
                    document_version=meta.document_version,
                    data=meta.model_dump(mode="json"),
                )
                await session.merge(doc)

    async def latest_document(self, proposal_id: str) -> DocumentMetadata | None:
        async with self._session_maker() as session:
            stmt = (
                select(DocumentModel)
                .where(DocumentModel.proposal_id == proposal_id)
                .order_by(DocumentModel.document_version.desc())
                .limit(1)
            )
            model = (await session.execute(stmt)).scalars().first()
            return DocumentMetadata.model_validate(model.data) if model else None

    async def list_documents(self, proposal_id: str) -> list[DocumentMetadata]:
        async with self._session_maker() as session:
            stmt = (
                select(DocumentModel)
                .where(DocumentModel.proposal_id == proposal_id)
                .order_by(DocumentModel.document_version)
            )
            result = await session.execute(stmt)
            return [DocumentMetadata.model_validate(m.data) for m in result.scalars().all()]

    # ---- idempotency -----------------------------------------------------------------
    async def get_idempotent(self, key: str, owner_id: str) -> dict[str, Any] | None:
        async with self._session_maker() as session:
            model = await session.get(IdempotencyModel, (key, owner_id))
            return model.response if model else None

    async def put_idempotent(self, key: str, owner_id: str, response: dict[str, Any]) -> None:
        async with self._session_maker() as session:
            async with session.begin():
                existing = await session.get(IdempotencyModel, (key, owner_id))
                if not existing:
                    idempotency_item = IdempotencyModel(
                        key=key,
                        owner_id=owner_id,
                        response=response,
                        created_at=utcnow(),
                    )
                    session.add(idempotency_item)