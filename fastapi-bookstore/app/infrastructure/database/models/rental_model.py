from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models import BaseModel


class RentalModel(BaseModel):
    __tablename__ = 'rental'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(100))
    rental_date: Mapped[datetime] = mapped_column(DateTime)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    return_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user: Mapped["UserModel"] = relationship(back_populates="rental_list")
    rental_details: Mapped[list["RentalDetailModel"]] = relationship(back_populates="rental", cascade="all, delete-orphan")