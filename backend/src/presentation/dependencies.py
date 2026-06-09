import os
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, sessionmaker

from application.dto.auth_dto import AuthenticatedUserDTO
from application.interfaces.clock import Clock
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.token_service import TokenService
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from application.use_cases.cancel_reservation import CancelReservationUseCase
from application.use_cases.create_reservation import CreateReservationUseCase
from application.use_cases.create_space import CreateSpaceUseCase
from application.use_cases.delete_space import DeleteSpaceUseCase
from application.use_cases.get_occupancy_by_space_report import (
    GetOccupancyBySpaceReportUseCase,
)
from application.use_cases.get_reservation import GetReservationUseCase
from application.use_cases.get_reservations_by_status_report import (
    GetReservationsByStatusReportUseCase,
)
from application.use_cases.get_revenue_by_range_report import (
    GetRevenueByRangeReportUseCase,
)
from application.use_cases.get_space import GetSpaceUseCase
from application.use_cases.get_space_availability import GetSpaceAvailabilityUseCase
from application.use_cases.list_reservations_by_space import (
    ListReservationsBySpaceUseCase,
)
from application.use_cases.list_spaces import ListSpacesUseCase
from application.use_cases.quote_reservation_cancellation import (
    QuoteReservationCancellationUseCase,
)
from application.use_cases.quote_reservation_price import QuoteReservationPriceUseCase
from application.use_cases.resolve_authenticated_user import (
    ResolveAuthenticatedUserUseCase,
)
from application.use_cases.update_space import UpdateSpaceUseCase
from domain.exceptions import AuthenticationError
from domain.services.cancellation_policy import CancellationPolicy
from domain.services.pricing_engine import PricingEngine
from infrastructure.clock import SystemClock
from infrastructure.db.session import build_session_factory
from infrastructure.security.jwt_token_service import JwtTokenService
from infrastructure.security.scrypt_password_hasher import ScryptPasswordHasher
from infrastructure.unit_of_work.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class JwtSettings:
    secret_key: str
    algorithm: str
    access_token_ttl_seconds: int
    issuer: str


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return build_session_factory()


@lru_cache
def get_jwt_settings() -> JwtSettings:
    secret_key = os.getenv("JWT_SECRET_KEY", "dev-only-change-in-production")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    ttl_raw = os.getenv("JWT_ACCESS_TOKEN_TTL_SECONDS", "3600")
    issuer = os.getenv("JWT_ISSUER", "cowork-reservations")

    try:
        access_token_ttl_seconds = int(ttl_raw)
    except ValueError as error:
        raise ValueError("JWT_ACCESS_TOKEN_TTL_SECONDS debe ser numerico") from error

    if access_token_ttl_seconds <= 0:
        raise ValueError("JWT_ACCESS_TOKEN_TTL_SECONDS debe ser mayor a cero")

    return JwtSettings(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_ttl_seconds=access_token_ttl_seconds,
        issuer=issuer,
    )


def get_clock() -> Clock:
    return SystemClock()


def get_pricing_engine() -> PricingEngine:
    return PricingEngine()


def get_cancellation_policy() -> CancellationPolicy:
    return CancellationPolicy()


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return ScryptPasswordHasher()


@lru_cache
def get_token_service() -> TokenService:
    settings = get_jwt_settings()
    return JwtTokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_ttl_seconds=settings.access_token_ttl_seconds,
        issuer=settings.issuer,
    )


def get_unit_of_work() -> SqlAlchemyUnitOfWork:
    session_factory = get_session_factory()
    return SqlAlchemyUnitOfWork(session_factory)


def get_access_token_ttl_seconds() -> int:
    return get_jwt_settings().access_token_ttl_seconds


def get_authenticate_user_use_case() -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        unit_of_work=get_unit_of_work(),
        password_hasher=get_password_hasher(),
        token_service=get_token_service(),
        access_token_ttl_seconds=get_access_token_ttl_seconds(),
    )


def get_resolve_authenticated_user_use_case() -> ResolveAuthenticatedUserUseCase:
    return ResolveAuthenticatedUserUseCase(
        unit_of_work=get_unit_of_work(),
        token_service=get_token_service(),
    )


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


def get_get_reservation_use_case() -> GetReservationUseCase:
    return GetReservationUseCase(get_unit_of_work())


def get_list_reservations_by_space_use_case() -> ListReservationsBySpaceUseCase:
    return ListReservationsBySpaceUseCase(get_unit_of_work())


def get_get_space_availability_use_case() -> GetSpaceAvailabilityUseCase:
    return GetSpaceAvailabilityUseCase(get_unit_of_work())


def get_get_occupancy_by_space_report_use_case() -> GetOccupancyBySpaceReportUseCase:
    return GetOccupancyBySpaceReportUseCase(get_unit_of_work())


def get_get_revenue_by_range_report_use_case() -> GetRevenueByRangeReportUseCase:
    return GetRevenueByRangeReportUseCase(get_unit_of_work())


def get_get_reservations_by_status_report_use_case() -> (
    GetReservationsByStatusReportUseCase
):
    return GetReservationsByStatusReportUseCase(get_unit_of_work())


def get_quote_reservation_price_use_case() -> QuoteReservationPriceUseCase:
    return QuoteReservationPriceUseCase(
        unit_of_work=get_unit_of_work(),
        pricing_engine=get_pricing_engine(),
        clock=get_clock(),
    )


def get_quote_reservation_cancellation_use_case() -> (
    QuoteReservationCancellationUseCase
):
    return QuoteReservationCancellationUseCase(
        unit_of_work=get_unit_of_work(),
        cancellation_policy=get_cancellation_policy(),
        clock=get_clock(),
    )


def get_cancel_reservation_use_case() -> CancelReservationUseCase:
    return CancelReservationUseCase(
        unit_of_work=get_unit_of_work(),
        cancellation_policy=get_cancellation_policy(),
        clock=get_clock(),
    )


bearer_scheme = HTTPBearer(auto_error=False)


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    use_case: ResolveAuthenticatedUserUseCase = Depends(
        get_resolve_authenticated_user_use_case
    ),
) -> AuthenticatedUserDTO:
    if credentials is None:
        raise AuthenticationError("Se requiere token de acceso")

    if credentials.scheme.lower() != "bearer":
        raise AuthenticationError("El esquema de autenticacion es invalido")

    return use_case.execute(credentials.credentials)
