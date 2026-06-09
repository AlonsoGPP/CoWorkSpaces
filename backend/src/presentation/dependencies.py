from functools import lru_cache

from sqlalchemy.orm import Session, sessionmaker

from application.interfaces.clock import Clock
from application.use_cases.cancel_reservation import CancelReservationUseCase
from application.use_cases.create_reservation import CreateReservationUseCase
from application.use_cases.create_space import CreateSpaceUseCase
from application.use_cases.delete_space import DeleteSpaceUseCase
from application.use_cases.get_space import GetSpaceUseCase
from application.use_cases.list_spaces import ListSpacesUseCase
from application.use_cases.update_space import UpdateSpaceUseCase
from domain.services.cancellation_policy import CancellationPolicy
from domain.services.pricing_engine import PricingEngine
from infrastructure.clock import SystemClock
from infrastructure.db.session import build_session_factory
from infrastructure.unit_of_work.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return build_session_factory()


def get_clock() -> Clock:
    return SystemClock()


def get_pricing_engine() -> PricingEngine:
    return PricingEngine()


def get_cancellation_policy() -> CancellationPolicy:
    return CancellationPolicy()


def get_unit_of_work() -> SqlAlchemyUnitOfWork:
    session_factory = get_session_factory()
    return SqlAlchemyUnitOfWork(session_factory)


def get_create_space_use_case() -> CreateSpaceUseCase:
    return CreateSpaceUseCase(get_unit_of_work())


def get_list_spaces_use_case() -> ListSpacesUseCase:
    return ListSpacesUseCase(get_unit_of_work())


def get_get_space_use_case() -> GetSpaceUseCase:
    return GetSpaceUseCase(get_unit_of_work())


def get_update_space_use_case() -> UpdateSpaceUseCase:
    return UpdateSpaceUseCase(get_unit_of_work())


def get_delete_space_use_case() -> DeleteSpaceUseCase:
    return DeleteSpaceUseCase(get_unit_of_work())


def get_create_reservation_use_case() -> CreateReservationUseCase:
    return CreateReservationUseCase(
        unit_of_work=get_unit_of_work(),
        pricing_engine=get_pricing_engine(),
        clock=get_clock(),
    )


def get_cancel_reservation_use_case() -> CancelReservationUseCase:
    return CancelReservationUseCase(
        unit_of_work=get_unit_of_work(),
        cancellation_policy=get_cancellation_policy(),
        clock=get_clock(),
    )
