from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

import pytest

from application.dto.pricing_dto import QuoteReservationPriceInputDTO
from application.use_cases.quote_reservation_price import QuoteReservationPriceUseCase
from domain.entities.reservation import Reservation
from domain.entities.space import Space
from domain.enums import SpaceStatus
from domain.exceptions import EntityNotFoundError, SpaceUnavailableError
from domain.services.pricing_engine import PricingEngine, PricingRuleName


@dataclass
class FakeClock:
    current: datetime

    def now(self) -> datetime:
        return self.current


class FakeSpaceRepository:
    def __init__(self, spaces: list[Space] | None = None) -> None:
        self._spaces = {space.id: space for space in spaces or []}

    def get_by_id(self, space_id: UUID) -> Space | None:
        return self._spaces.get(space_id)

    def list_all(self) -> list[Space]:
        return list(self._spaces.values())

    def add(self, space: Space) -> Space:
        self._spaces[space.id] = space
        return space

    def update(self, space: Space) -> Space:
        self._spaces[space.id] = space
        return space

    def delete(self, space_id: UUID) -> None:
        self._spaces.pop(space_id, None)


class FakeReservationRepository:
    def add(self, reservation: Reservation) -> Reservation:
        return reservation

    def get_by_id(self, reservation_id: UUID) -> Reservation | None:
        return None

    def list_by_space(self, space_id: UUID) -> list[Reservation]:
        return []

    def update(self, reservation: Reservation) -> Reservation:
        return reservation


class FakeUnitOfWork:
    def __init__(
        self,
        *,
        space_repository: FakeSpaceRepository,
        reservation_repository: FakeReservationRepository,
    ) -> None:
        self._space_repository = space_repository
        self._reservation_repository = reservation_repository

    @property
    def space_repository(self) -> FakeSpaceRepository:
        return self._space_repository

    @property
    def reservation_repository(self) -> FakeReservationRepository:
        return self._reservation_repository

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


def _space(status: SpaceStatus = SpaceStatus.ACTIVO) -> Space:
    return Space(
        id=uuid4(),
        name="Sala Quote",
        status=status,
        hourly_rate=Decimal("100"),
        capacity=10,
    )


def test_quote_reservation_price_happy_path() -> None:
    space = _space()
    use_case = QuoteReservationPriceUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository(),
        ),
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    output = use_case.execute(
        QuoteReservationPriceInputDTO(
            space_id=space.id,
            start_at=datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 13, 15, 0, tzinfo=timezone.utc),
        )
    )

    assert output.space_id == space.id
    assert output.base_hourly_rate == Decimal("100")
    assert output.total_price == Decimal("614.53")
    assert output.applied_rules == (
        PricingRuleName.HORA_PICO,
        PricingRuleName.FIN_DE_SEMANA,
        PricingRuleName.RESERVA_LARGA,
        PricingRuleName.ANTICIPACION,
    )


def test_quote_reservation_price_space_not_found() -> None:
    use_case = QuoteReservationPriceUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository([]),
            reservation_repository=FakeReservationRepository(),
        ),
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            QuoteReservationPriceInputDTO(
                space_id=uuid4(),
                start_at=datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 13, 15, 0, tzinfo=timezone.utc),
            )
        )


def test_quote_reservation_price_space_in_maintenance() -> None:
    space = _space(status=SpaceStatus.MANTENIMIENTO)
    use_case = QuoteReservationPriceUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository(),
        ),
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(SpaceUnavailableError):
        use_case.execute(
            QuoteReservationPriceInputDTO(
                space_id=space.id,
                start_at=datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 13, 15, 0, tzinfo=timezone.utc),
            )
        )
