from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.catalog.models.model_base import Base
#from src.catalog.models.family import FamilyModel


class BusinessLineModel(Base):
    __tablename__ = "business_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    families: Mapped[List["FamilyModel"]] = relationship(back_populates="business_line", cascade="all, delete-orphan")
