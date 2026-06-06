from collections.abc import Callable

from sqlalchemy.orm import Session

from domain.repositories.reservation_repository import ReservationRepository
from domain.repositories.space_repository import SpaceRepository
from infrastructure.repositories.sqlalchemy_reservation_repository import (
    SqlAlchemyReservationRepository,
)
from infrastructure.repositories.sqlalchemy_space_repository import (
    SqlAlchemySpaceRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._space_repository: SqlAlchemySpaceRepository | None = None
        self._reservation_repository: SqlAlchemyReservationRepository | None = None

    @property
    def space_repository(self) -> SpaceRepository:
        if self._space_repository is None:
            raise RuntimeError("La unidad de trabajo no fue iniciada")
        return self._space_repository

    @property
    def reservation_repository(self) -> ReservationRepository:
        if self._reservation_repository is None:
            raise RuntimeError("La unidad de trabajo no fue iniciada")
        return self._reservation_repository

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._space_repository = SqlAlchemySpaceRepository(self._session)
        self._reservation_repository = SqlAlchemyReservationRepository(self._session)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if exc_type is not None:
            self.rollback()
        if self._session is not None:
            self._session.close()
        self._session = None
        self._space_repository = None
        self._reservation_repository = None

    def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("No existe una sesion activa")
        self._session.commit()

    def rollback(self) -> None:
        if self._session is None:
            return
        self._session.rollback()
