from datetime import datetime
from dataclasses import dataclass
from uuid import uuid4

from app.domain.enums import UserStatus, UserRegistrationStatus


@dataclass
class User:
    id: int | None
    user_id: str
    ext_user_id: str| None
    first_name: str
    last_name: str | None
    email: str
    phone: str
    status: UserStatus | str
    registration_status: UserRegistrationStatus | str
    created_at: datetime

    def __init__(
            self,
            id: int | None,
            user_id: str,
            ext_user_id: str | None,
            first_name: str,
            last_name: str | None,
            email: str,
            phone: str,
            status: UserStatus | str,
            registration_status: UserRegistrationStatus | str,
            created_at: datetime):
        self.id = id
        self.user_id = user_id
        self.ext_user_id = ext_user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.status = status
        self.registration_status = registration_status
        self.created_at = created_at

    @staticmethod
    def create(
            email: str,
            first_name: str,
            last_name: str,
            phone: str,
    ) -> "User":
        return User(
            id=None,
            user_id=str(uuid4()),
            ext_user_id=None,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            status=UserStatus.CREATED,
            registration_status=UserRegistrationStatus.PENDING,
            created_at=datetime.now(),
        )