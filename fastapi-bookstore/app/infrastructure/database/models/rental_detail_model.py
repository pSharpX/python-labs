from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models import BaseModel

class RentalDetailModel(BaseModel):
    __tablename__ = 'rental_detail'

    id: Mapped[int] = mapped_column(primary_key=True)
    return_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    rental_id: Mapped[int] = mapped_column(ForeignKey('rental.id'))
    book_copy_id: Mapped[int] = mapped_column(ForeignKey('books_copy.id'))

    rental: Mapped["RentalModel"] = relationship(back_populates="rental_details")
    book_copy: Mapped["BookCopyModel"] = relationship(back_populates="rental_details")