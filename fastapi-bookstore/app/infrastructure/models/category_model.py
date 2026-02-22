from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from app.infrastructure.models import BaseModel

class CategoryModel(BaseModel):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    books: Mapped[list["BookModel"]] = relationship(back_populates="category", cascade="all, delete-orphan")