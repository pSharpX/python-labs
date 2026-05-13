from datetime import datetime, UTC
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.infrastructure.database.models.base_model import BaseModel


class OutboxModel(BaseModel):
    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON)
    processed: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC)
    )