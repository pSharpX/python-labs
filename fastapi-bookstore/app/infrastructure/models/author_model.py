from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column
from app.infrastructure.models import BaseModel

class AuthorModel(BaseModel):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    books: Mapped[list["BookModel"]] = relationship(back_populates="author", cascade="all, delete-orphan")