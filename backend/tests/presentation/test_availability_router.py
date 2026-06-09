from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.availability_dto import (
    SpaceAvailabilityOutputDTO,
    SpaceAvailabilityReservationItemDTO,
    SpaceAvailabilitySlotItemDTO,
)
from domain.enums import ReservationStatus, SpaceStatus
from domain.exceptions import EntityNotFoundError
from presentation.api import create_app
from presentation.dependencies import get_get_space_availability_use_case


def _availability_output() -> SpaceAvailabilityOutputDTO:
    return SpaceAvailabilityOutputDTO(
        space_id=uuid4(),
        space_name="Sala Norte",
        space_status=SpaceStatus.ACTIVO,
        start_at=datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc),
        slot_minutes=30,
        total_slots=6,
        available_slots=4,
        availability_percentage=Decimal("66.67"),
        reservations=(
            SpaceAvailabilityReservationItemDTO(
                reservation_id=uuid4(),
                start_at=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 20, 11, 0, tzinfo=timezone.utc),
                status=ReservationStatus.CONFIRMADA,
                total_price=Decimal("200.00"),
                blocks_availability=True,
            ),
        ),
        slots=(
            SpaceAvailabilitySlotItemDTO(
                start_at=datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 20, 9, 30, tzinfo=timezone.utc),
                is_available=True,
                overlapping_reservations_count=0,
            ),
            SpaceAvailabilitySlotItemDTO(
                start_at=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
                end_at=datetime(2026, 6, 20, 10, 30, tzinfo=timezone.utc),
                is_available=False,
                overlapping_reservations_count=1,
            ),
        ),
    )


def test_get_space_availability_returns_ok() -> None:
    app = create_app()
    output = _availability_output()

    class StubUseCase:
        def execute(self, input_dto: object) -> SpaceAvailabilityOutputDTO:
            return output

    app.dependency_overrides[get_get_space_availability_use_case] = StubUseCase
    client = TestClient(app)

    response = client.get(
        f"/availability/by-space/{output.space_id}?start_at=2026-06-20T09:00:00%2B00:00&end_at=2026-06-20T12:00:00%2B00:00&slot_minutes=30"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["space_name"] == "Sala Norte"
    assert payload["availability_percentage"] == "66.67"
    assert payload["slots"][1]["is_available"] is False


def test_get_space_availability_returns_not_found() -> None:
    app = create_app()

    class StubUseCase:
        def execute(self, input_dto: object) -> SpaceAvailabilityOutputDTO:
            raise EntityNotFoundError("Espacio no encontrado")

    app.dependency_overrides[get_get_space_availability_use_case] = StubUseCase
    client = TestClient(app)

    response = client.get(
        f"/availability/by-space/{uuid4()}?start_at=2026-06-20T09:00:00%2B00:00&end_at=2026-06-20T12:00:00%2B00:00"
    )

    assert response.status_code == 404


def test_get_space_availability_returns_422_on_invalid_slot_minutes() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get(
        f"/availability/by-space/{uuid4()}?start_at=2026-06-20T09:00:00%2B00:00&end_at=2026-06-20T12:00:00%2B00:00&slot_minutes=7"
    )

    assert response.status_code == 422
