from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFound
from app.domain.entities import User
from app.domain.repositories import UserRepository
from app.infrastructure.models import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        db_user = UserModel(ext_user_id=user.ext_user_id, first_name=user.first_name, last_name=user.last_name, email=user.email,
                            phone=user.phone, status=user.status, created_at=user.created_at)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return User(id=db_user.id, ext_user_id=db_user.ext_user_id, first_name=db_user.first_name, last_name=db_user.last_name, email=db_user.email,
                    phone=db_user.phone, status=db_user.status, created_at=db_user.created_at)

    def update(self, user_id: int, user: User):
        stmt = select(User).where(User.id == user_id)
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

    def get_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id)
        db_user = self.db.execute(stmt).first()
        if not db_user:
            raise UserNotFound(f"{user_id}")

        return User(id=db_user.id, ext_user_id=db_user.ext_user_id, first_name=db_user.first_name,
                    last_name=db_user.last_name, email=db_user.email,
                    phone=db_user.phone, status=db_user.status, created_at=db_user.created_at)

    def get_by_ext_user_id(self, ext_user_id: str):
        stmt = select(User).where(User.ext_user_id == ext_user_id)
        db_user = self.db.execute(stmt).first()
        if not db_user:
            return None

        return User(id=db_user.id, ext_user_id=db_user.ext_user_id, first_name=db_user.first_name,
                    last_name=db_user.last_name, email=db_user.email,
                    phone=db_user.phone, status=db_user.status, created_at=db_user.created_at)
