from datetime import datetime
from typing import Any

from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.proposal_record import RunState
from src.models.base import Base


class ProposalModel(Base):
    __tablename__ = "proposals"

    proposal_id: Mapped[str] = mapped_column(String, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    run_state: Mapped[str] = mapped_column(String, nullable=False, default=RunState.IDLE)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)