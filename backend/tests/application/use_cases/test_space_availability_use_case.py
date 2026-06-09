from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

import pytest

from application.dto.availability_dto import SpaceAvailabilityInputDTO
from application.use_cases.get_space_availability import GetSpaceAvailabilityUseCase
from domain.entities.reservation import Reservation
from domain.entities.space import Space
from domain.enums import ReservationStatus, SpaceStatus
from domain.exceptions import EntityNotFoundError
from domain.value_objects.reservation_window import ReservationWindow


class FakeSpaceRepository:
    def __init__(self, spaces: list[Space] | None = None) -> None:
        self._spaces = {space.id: space for space in spaces or []}

    def get_by_id(self, space_id: UUID) -> Space | None:
        return self._spaces.get(space_id)


class FakeReservationRepository:
    def __init__(self, reservations: list[Reservation] | None = None) -> None:
        self._reservations = reservations or []

    def list_by_space_in_range(
        self,
        space_id: UUID,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Reservation]:
        return [
            reservation
            for reservation in self._reservations
            if reservation.space_id == space_id
            and reservation.reservation_window.start_at < end_at
            and reservation.reservation_window.end_at > start_at
        ]


@dataclass
class FakeUnitOfWork:
    space_repository: FakeSpaceRepository
    reservation_repository: FakeReservationRepository

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


def _space() -> Space:
    return Space(
        id=uuid4(),
        name="Sala Disponibilidad",
        status=SpaceStatus.ACTIVO,
        hourly_rate=Decimal("120.00"),
        capacity=8,
    )


def _reservation(
    *,
    space_id: UUID,
    start_at: datetime,
    end_at: datetime,
    status: ReservationStatus,
) -> Reservation:
    return Reservation.create(
        space_id=space_id,
        reservation_window=ReservationWindow(start_at=start_at, end_at=end_at),
        total_price=Decimal("200.00"),
        status=status,
    )


def test_get_space_availability_returns_slots_and_percentage() -> None:
    space = _space()

    confirmed_reservation = _reservation(
        space_id=space.id,
        start_at=datetime(2026, 6, 15, 10, 30, tzinfo=timezone.utc),
        end_at=datetime(2026, 6, 15, 11, 30, tzinfo=timezone.utc),
        status=ReservationStatus.CONFIRMADA,
    )
    cancelled_reservation = _reservation(
        space_id=space.id,
        start_at=datetime(2026, 6, 15, 11, 30, tzinfo=timezone.utc),
        end_at=datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc),
        status=ReservationStatus.CANCELADA,
    )

    use_case = GetSpaceAvailabilityUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository(
                [confirmed_reservation, cancelled_reservation]
            ),
        )
    )

    output = use_case.execute(
        SpaceAvailabilityInputDTO(
            space_id=space.id,
            start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc),
            slot_minutes=30,
        )
    )

    assert output.total_slots == 4
    assert output.available_slots == 2
    assert output.availability_percentage == Decimal("50.00")
    assert len(output.reservations) == 2
    assert output.reservations[0].blocks_availability is True
    assert output.reservations[1].blocks_availability is False


def test_get_space_availability_fails_when_space_does_not_exist() -> None:
    use_case = GetSpaceAvailabilityUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository([]),
            reservation_repository=FakeReservationRepository([]),
        )
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            SpaceAvailabilityInputDTO(
                space_id=uuid4(),
                start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc),
                slot_minutes=30,
            )
        )
