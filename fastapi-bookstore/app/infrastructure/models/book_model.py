from typing import Optional
from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.models import BaseModel

class BookModel(BaseModel):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    rating: Mapped[int] = mapped_column(Integer)
    published_date: Mapped[int] = mapped_column(Integer)

    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))

    author: Mapped["AuthorModel"] = relationship(back_populates="books")
    category: Mapped["CategoryModel"] = relationship(back_populates="books")