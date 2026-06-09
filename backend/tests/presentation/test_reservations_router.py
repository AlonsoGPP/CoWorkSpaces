from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.reservation_dto import ReservationOutputDTO
from domain.enums import ReservationStatus
from domain.exceptions import EntityNotFoundError
from presentation.api import create_app
from presentation.dependencies import (
    get_get_reservation_use_case,
    get_list_reservations_by_space_use_case,
)


def _reservation_output() -> ReservationOutputDTO:
    return ReservationOutputDTO(
        id=uuid4(),
        space_id=uuid4(),
        start_at=datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc),
        status=ReservationStatus.CONFIRMADA,
        total_price=Decimal("200.00"),
        created_at=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        cancelled_at=None,
    )


def test_get_reservation_returns_ok() -> None:
    app = create_app(enable_auth=False)
    reservation_output = _reservation_output()

    class StubGetReservationUseCase:
        def execute(self, reservation_id: object) -> ReservationOutputDTO:
            return reservation_output

    app.dependency_overrides[get_get_reservation_use_case] = StubGetReservationUseCase
    client = TestClient(app)

    response = client.get(f"/reservations/{reservation_output.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(reservation_output.id)


def test_get_reservation_returns_not_found() -> None:
    app = create_app(enable_auth=False)

    class StubGetReservationUseCase:
        def execute(self, reservation_id: object) -> ReservationOutputDTO:
            raise EntityNotFoundError("Reserva no encontrada")

    app.dependency_overrides[get_get_reservation_use_case] = StubGetReservationUseCase
    client = TestClient(app)

    response = client.get(f"/reservations/{uuid4()}")

    assert response.status_code == 404


def test_list_reservations_by_space_returns_ok() -> None:
    app = create_app(enable_auth=False)
    reservation_output = _reservation_output()

    class StubListReservationsBySpaceUseCase:
        def execute(self, space_id: object) -> list[ReservationOutputDTO]:
            return [reservation_output]

    app.dependency_overrides[get_list_reservations_by_space_use_case] = (
        StubListReservationsBySpaceUseCase
    )
    client = TestClient(app)

    response = client.get(f"/reservations/by-space/{reservation_output.space_id}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == str(reservation_output.id)


def test_list_reservations_by_space_returns_not_found() -> None:
    app = create_app(enable_auth=False)

    class StubListReservationsBySpaceUseCase:
        def execute(self, space_id: object) -> list[ReservationOutputDTO]:
            raise EntityNotFoundError("Espacio no encontrado")

    app.dependency_overrides[get_list_reservations_by_space_use_case] = (
        StubListReservationsBySpaceUseCase
    )
    client = TestClient(app)

    response = client.get(f"/reservations/by-space/{uuid4()}")

    assert response.status_code == 404
