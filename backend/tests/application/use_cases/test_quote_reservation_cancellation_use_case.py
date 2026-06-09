from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

import pytest

from application.dto.cancellation_dto import QuoteReservationCancellationInputDTO
from application.use_cases.quote_reservation_cancellation import (
    QuoteReservationCancellationUseCase,
)
from domain.entities.reservation import Reservation
from domain.entities.space import Space
from domain.enums import ReservationStatus, SpaceStatus
from domain.exceptions import EntityNotFoundError, ReservationNotCancelableError
from domain.services.cancellation_policy import CancellationPolicy, RefundTier
from domain.value_objects.reservation_window import ReservationWindow


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
    def __init__(self, reservations: list[Reservation] | None = None) -> None:
        self._reservations = {
            reservation.id: reservation for reservation in reservations or []
        }

    def add(self, reservation: Reservation) -> Reservation:
        self._reservations[reservation.id] = reservation
        return reservation

    def get_by_id(self, reservation_id: UUID) -> Reservation | None:
        return self._reservations.get(reservation_id)

    def list_by_space(self, space_id: UUID) -> list[Reservation]:
        return [
            reservation
            for reservation in self._reservations.values()
            if reservation.space_id == space_id
        ]

    def update(self, reservation: Reservation) -> Reservation:
        self._reservations[reservation.id] = reservation
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


def _space() -> Space:
    return Space(
        id=uuid4(),
        name="Sala Cancel",
        status=SpaceStatus.ACTIVO,
        hourly_rate=Decimal("100"),
        capacity=6,
    )


def _reservation(*, space_id: UUID, status: ReservationStatus) -> Reservation:
    return Reservation.create(
        space_id=space_id,
        reservation_window=ReservationWindow(
            start_at=datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
        ),
        total_price=Decimal("200.00"),
        status=status,
    )


def test_quote_reservation_cancellation_happy_path() -> None:
    space = _space()
    reservation = _reservation(space_id=space.id, status=ReservationStatus.CONFIRMADA)
    use_case = QuoteReservationCancellationUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository([reservation]),
        ),
        cancellation_policy=CancellationPolicy(),
        clock=FakeClock(datetime(2026, 7, 7, 8, 0, tzinfo=timezone.utc)),
    )

    output = use_case.execute(
        QuoteReservationCancellationInputDTO(reservation_id=reservation.id)
    )

    assert output.reservation_id == reservation.id
    assert output.refund_amount == Decimal("200.00")
    assert output.refund_rate == Decimal("1")
    assert output.refund_tier == RefundTier.COMPLETO


def test_quote_reservation_cancellation_not_found() -> None:
    use_case = QuoteReservationCancellationUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository(),
            reservation_repository=FakeReservationRepository(),
        ),
        cancellation_policy=CancellationPolicy(),
        clock=FakeClock(datetime(2026, 7, 7, 8, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(QuoteReservationCancellationInputDTO(reservation_id=uuid4()))


def test_quote_reservation_cancellation_completed_reservation() -> None:
    space = _space()
    reservation = _reservation(space_id=space.id, status=ReservationStatus.COMPLETADA)
    use_case = QuoteReservationCancellationUseCase(
        unit_of_work=FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository([reservation]),
        ),
        cancellation_policy=CancellationPolicy(),
        clock=FakeClock(datetime(2026, 7, 7, 8, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(ReservationNotCancelableError):
        use_case.execute(
            QuoteReservationCancellationInputDTO(reservation_id=reservation.id)
        )
