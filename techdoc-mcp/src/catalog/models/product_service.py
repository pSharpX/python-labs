from typing import Optional

from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.catalog.models.model_base import Base
#from src.catalog.models.family import FamilyModel


class ProductServiceModel(Base):
    __tablename__ = "products_services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    smb_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    corp_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    family: Mapped["FamilyModel"] = relationship(back_populates="products_services")