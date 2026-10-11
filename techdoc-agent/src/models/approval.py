from datetime import datetime
from typing import Any

from sqlalchemy import Integer, DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)