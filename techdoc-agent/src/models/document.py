from typing import Any

from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import mapped_column, Mapped

from src.models.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    document_version: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)