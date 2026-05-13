from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFound
from app.domain.entities import User
from app.application.ports.repositories import UserRepository
from app.infrastructure.database.models import UserModel
from app.domain.enums import UserRegistrationStatus


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        db_user = UserModel(
            user_id=user.user_id,
            ext_user_id=user.ext_user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            status=user.status,
            registration_status=user.registration_status,
            created_at=user.created_at
        )
        self.db.add(db_user)

        return User(
            id=db_user.id,
            user_id=db_user.user_id,
            ext_user_id=db_user.ext_user_id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            phone=db_user.phone,
            status=db_user.status,
            registration_status=db_user.registration_status,
            created_at=db_user.created_at
        )

    def update(self, user_id: int, user: User):
        stmt = select(UserModel).where(UserModel.id == user_id)
        db_user = self.db.execute(stmt).first()
        if not db_user:
            raise UserNotFound(f"{user_id}")

        db_user.ext_user_id = user.ext_user_id
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.email = user.email
        db_user.phone = user.phone
        db_user.status = user.status

        self.db.commit()
        self.db.refresh(db_user)

    def mark_as_synced(self, user_id: str, ext_user_id: str):
        stmt = (
            update(UserModel)
            .where(UserModel.user_id == user_id)
            .values(
                registration_status=UserRegistrationStatus.SYNCED,
                ext_user_id=ext_user_id,
            )
        )
        self.db.execute(stmt)

    def mark_as_failed(self, user_id: str):
        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(
                registration_status=UserRegistrationStatus.FAILED,
            )
        )
        self.db.execute(stmt)

    def get_by_id(self, user_id: int):
        stmt = select(UserModel).where(UserModel.id == user_id)
        db_user = self.db.execute(stmt).first()
        if not db_user:
            raise UserNotFound(f"{user_id}")

        return User(
            id=db_user.id,
            user_id=db_user.user_id,
            ext_user_id=db_user.ext_user_id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            phone=db_user.phone,
            status=db_user.status,
            registration_status=db_user.registration_status,
            created_at=db_user.created_at
        )

    def get_by_user_id(self, user_id: str):
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        db_user = self.db.execute(stmt).first()
        if not db_user:
            return None

        return User(
            id=db_user.id,
            user_id=db_user.user_id,
            ext_user_id=db_user.ext_user_id,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            email=db_user.email,
            phone=db_user.phone,
            status=db_user.status,
            registration_status=db_user.registration_status,
            created_at=db_user.created_at
        )
