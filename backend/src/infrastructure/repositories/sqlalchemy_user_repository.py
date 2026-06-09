from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            return None
        return self._to_domain(model)

    def get_by_email(self, email: str) -> User | None:
        normalized_email = email.strip().lower()
        row = self._session.scalars(
            select(UserModel).where(UserModel.email == normalized_email)
        ).first()
        if row is None:
            return None
        return self._to_domain(row)

    def add(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            is_active=model.is_active,
            created_at=model.created_at,
        )
