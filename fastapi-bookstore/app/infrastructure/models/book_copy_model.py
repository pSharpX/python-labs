from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models import BaseModel


class BookCopyModel(BaseModel):
    __tablename__ = 'books_copy'

    id: Mapped[int] = mapped_column(primary_key=True)
    physical_identifier: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(100))
    acquisition_date: Mapped[datetime] = mapped_column(DateTime)

    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))

    book: Mapped["BookModel"] = relationship(back_populates="books_copy")