from datetime import datetime
from typing import Any

from sqlalchemy import String, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    artifact_type: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    based_on: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)