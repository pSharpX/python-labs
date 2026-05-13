from typing import Optional
from datetime import datetime
from sqlalchemy import DateTime,String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True)
    ext_user_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(30), unique=True)
    phone: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30))
    registration_status: Mapped[str] = mapped_column("user_registration_status", String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    rental_list: Mapped[list["RentalModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")