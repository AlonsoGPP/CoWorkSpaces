from typing import Protocol

from application.interfaces.reporting_repository import ReportingRepository
from domain.repositories.reservation_repository import ReservationRepository
from domain.repositories.space_repository import SpaceRepository
from domain.repositories.user_repository import UserRepository


class UnitOfWork(Protocol):
    @property
    def space_repository(self) -> SpaceRepository: ...

    @property
    def reservation_repository(self) -> ReservationRepository: ...

    @property
    def user_repository(self) -> UserRepository: ...

    @property
    def reporting_repository(self) -> ReportingRepository: ...

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
