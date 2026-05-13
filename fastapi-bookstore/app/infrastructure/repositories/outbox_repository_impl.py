from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.infrastructure.database.models import OutboxModel
from app.application.ports.repositories import OutboxRepository


class OutboxRepositoryImpl(OutboxRepository):

    def __init__(self, db: Session):
        self.db = db

    def add(self, event_type: str, payload: dict) -> None:
        model = OutboxModel(event_type=event_type, payload=payload)
        self.db.add(model)

    def get_unprocessed(self) -> list:
        stmt = select(OutboxModel).where(OutboxModel.processed == False)
        results = self.db.execute(stmt)
        return results.scalars().all()

    def mark_processed(self, event_id: int) -> None:
        stmt = (
            update(OutboxModel)
            .where(OutboxModel.id == event_id)
            .values(
                processed=True,
            )
        )
        self.db.execute(stmt)

