from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.catalog.models.model_base import Base
from src.catalog.models.business_line import BusinessLineModel
from src.catalog.models.product_service import ProductServiceModel


class FamilyModel(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    line_id: Mapped[int] = mapped_column(ForeignKey("business_lines.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    business_line: Mapped["BusinessLineModel"] = relationship(back_populates="families")
    products_services: Mapped[List["ProductServiceModel"]] = relationship(back_populates="family", cascade="all, delete-orphan")
