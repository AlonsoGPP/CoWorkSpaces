from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

import pytest

from application.dto.reservation_dto import (
    CancelReservationInputDTO,
    CreateReservationInputDTO,
)
from application.use_cases.cancel_reservation import CancelReservationUseCase
from application.use_cases.create_reservation import CreateReservationUseCase
from application.use_cases.get_reservation import GetReservationUseCase
from application.use_cases.list_reservations_by_space import (
    ListReservationsBySpaceUseCase,
)
from domain.entities.reservation import Reservation
from domain.entities.space import Space
from domain.enums import ReservationStatus, SpaceStatus
from domain.exceptions import (
    EntityNotFoundError,
    OverlappingReservationError,
    SpaceUnavailableError,
)
from domain.services.cancellation_policy import CancellationPolicy
from domain.services.pricing_engine import PricingEngine
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
        self.raise_overlap = False

    def add(self, reservation: Reservation) -> Reservation:
        if self.raise_overlap:
            raise OverlappingReservationError("Conflicto de solapamiento")
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
        self.committed = False

    @property
    def space_repository(self) -> FakeSpaceRepository:
        return self._space_repository

    @property
    def reservation_repository(self) -> FakeReservationRepository:
        return self._reservation_repository

    def __enter__(self) -> Self:
        self.committed = False
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


def _space(status: SpaceStatus = SpaceStatus.ACTIVO) -> Space:
    return Space(
        id=uuid4(),
        name="Sala A",
        status=status,
        hourly_rate=Decimal("100"),
        capacity=6,
    )


def test_create_reservation_happy_path() -> None:
    space = _space()
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository([space]),
        reservation_repository=FakeReservationRepository(),
    )
    use_case = CreateReservationUseCase(
        unit_of_work=uow,
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    output = use_case.execute(
        CreateReservationInputDTO(
            space_id=space.id,
            start_at=datetime(2026, 6, 2, 20, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 2, 22, 0, tzinfo=timezone.utc),
        )
    )

    assert output.space_id == space.id
    assert output.status == ReservationStatus.CONFIRMADA
    assert output.total_price == Decimal("200.00")
    assert uow.committed is True


def test_create_reservation_fails_when_space_not_found() -> None:
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository([]),
        reservation_repository=FakeReservationRepository(),
    )
    use_case = CreateReservationUseCase(
        unit_of_work=uow,
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            CreateReservationInputDTO(
                space_id=uuid4(),
                start_at=datetime(2026, 6, 2, 20, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 2, 22, 0, tzinfo=timezone.utc),
            )
        )


def test_create_reservation_fails_when_space_is_in_maintenance() -> None:
    space = _space(status=SpaceStatus.MANTENIMIENTO)
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository([space]),
        reservation_repository=FakeReservationRepository(),
    )
    use_case = CreateReservationUseCase(
        unit_of_work=uow,
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(SpaceUnavailableError):
        use_case.execute(
            CreateReservationInputDTO(
                space_id=space.id,
                start_at=datetime(2026, 6, 2, 20, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 2, 22, 0, tzinfo=timezone.utc),
            )
        )


def test_create_reservation_fails_on_overlap() -> None:
    space = _space()
    reservation_repository = FakeReservationRepository()
    reservation_repository.raise_overlap = True
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository([space]),
        reservation_repository=reservation_repository,
    )
    use_case = CreateReservationUseCase(
        unit_of_work=uow,
        pricing_engine=PricingEngine(),
        clock=FakeClock(datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(OverlappingReservationError):
        use_case.execute(
            CreateReservationInputDTO(
                space_id=space.id,
                start_at=datetime(2026, 6, 2, 20, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 2, 22, 0, tzinfo=timezone.utc),
            )
        )


def test_cancel_reservation_happy_path() -> None:
    space = _space()
    reservation = Reservation.create(
        space_id=space.id,
        reservation_window=ReservationWindow(
            start_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
        ),
        total_price=Decimal("200.00"),
    )
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository([space]),
        reservation_repository=FakeReservationRepository([reservation]),
    )
    use_case = CancelReservationUseCase(
        unit_of_work=uow,
        cancellation_policy=CancellationPolicy(),
        clock=FakeClock(datetime(2026, 6, 7, 8, 0, tzinfo=timezone.utc)),
    )

    output = use_case.execute(CancelReservationInputDTO(reservation_id=reservation.id))

    assert output.reservation.status == ReservationStatus.CANCELADA
    assert output.refund_amount == Decimal("200.00")
    assert uow.committed is True


def test_cancel_reservation_fails_when_not_found() -> None:
    uow = FakeUnitOfWork(
        space_repository=FakeSpaceRepository(),
        reservation_repository=FakeReservationRepository(),
    )
    use_case = CancelReservationUseCase(
        unit_of_work=uow,
        cancellation_policy=CancellationPolicy(),
        clock=FakeClock(datetime(2026, 6, 7, 8, 0, tzinfo=timezone.utc)),
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(CancelReservationInputDTO(reservation_id=uuid4()))


def test_get_reservation_happy_path() -> None:
    space = _space()
    reservation = Reservation.create(
        space_id=space.id,
        reservation_window=ReservationWindow(
            start_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
        ),
        total_price=Decimal("200.00"),
    )
    use_case = GetReservationUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space]),
            reservation_repository=FakeReservationRepository([reservation]),
        )
    )

    output = use_case.execute(reservation.id)

    assert output.id == reservation.id
    assert output.space_id == space.id


def test_get_reservation_fails_when_not_found() -> None:
    use_case = GetReservationUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository(),
            reservation_repository=FakeReservationRepository(),
        )
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(uuid4())


def test_list_reservations_by_space_happy_path() -> None:
    space = _space()
    other_space = _space()
    reservation_a = Reservation.create(
        space_id=space.id,
        reservation_window=ReservationWindow(
            start_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
        ),
        total_price=Decimal("200.00"),
    )
    reservation_b = Reservation.create(
        space_id=other_space.id,
        reservation_window=ReservationWindow(
            start_at=datetime(2026, 6, 11, 10, 0, tzinfo=timezone.utc),
            end_at=datetime(2026, 6, 11, 12, 0, tzinfo=timezone.utc),
        ),
        total_price=Decimal("200.00"),
    )
    use_case = ListReservationsBySpaceUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository([space, other_space]),
            reservation_repository=FakeReservationRepository(
                [reservation_a, reservation_b]
            ),
        )
    )

    output = use_case.execute(space.id)

    assert len(output) == 1
    assert output[0].id == reservation_a.id


def test_list_reservations_by_space_fails_when_space_not_found() -> None:
    use_case = ListReservationsBySpaceUseCase(
        FakeUnitOfWork(
            space_repository=FakeSpaceRepository(),
            reservation_repository=FakeReservationRepository(),
        )
    )

    with pytest.raises(EntityNotFoundError):
        use_case.execute(uuid4())
