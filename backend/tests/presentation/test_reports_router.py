from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.report_dto import (
    OccupancyBySpaceItemDTO,
    OccupancyBySpaceReportOutputDTO,
    ReservationsByStatusItemDTO,
    ReservationsByStatusReportOutputDTO,
    RevenueByRangeReportOutputDTO,
)
from domain.enums import ReservationStatus
from presentation.api import create_app
from presentation.dependencies import (
    get_get_occupancy_by_space_report_use_case,
    get_get_reservations_by_status_report_use_case,
    get_get_revenue_by_range_report_use_case,
)


def test_get_occupancy_by_space_report_returns_ok() -> None:
    app = create_app(enable_auth=False)
    output = OccupancyBySpaceReportOutputDTO(
        start_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
        total_minutes_in_range=Decimal("120.00"),
        items=(
            OccupancyBySpaceItemDTO(
                space_id=uuid4(),
                space_name="Sala A",
                occupied_minutes=Decimal("60.00"),
                occupancy_percentage=Decimal("50.00"),
                reservations_count=2,
            ),
        ),
    )

    class StubUseCase:
        def execute(self, input_dto: object) -> OccupancyBySpaceReportOutputDTO:
            return output

    app.dependency_overrides[get_get_occupancy_by_space_report_use_case] = StubUseCase
    client = TestClient(app)

    response = client.get(
        "/reports/occupancy-by-space?start_at=2026-07-01T10:00:00%2B00:00&end_at=2026-07-01T12:00:00%2B00:00"
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["occupancy_percentage"] == "50.00"


def test_get_revenue_by_range_report_returns_ok() -> None:
    app = create_app(enable_auth=False)
    output = RevenueByRangeReportOutputDTO(
        start_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
        total_revenue=Decimal("999.99"),
    )

    class StubUseCase:
        def execute(self, input_dto: object) -> RevenueByRangeReportOutputDTO:
            return output

    app.dependency_overrides[get_get_revenue_by_range_report_use_case] = StubUseCase
    client = TestClient(app)

    response = client.get(
        "/reports/revenue?start_at=2026-07-01T10:00:00%2B00:00&end_at=2026-07-01T12:00:00%2B00:00"
    )

    assert response.status_code == 200
    assert response.json()["total_revenue"] == "999.99"


def test_get_reservations_by_status_report_returns_ok() -> None:
    app = create_app(enable_auth=False)
    output = ReservationsByStatusReportOutputDTO(
        start_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
        total_reservations=3,
        items=(
            ReservationsByStatusItemDTO(status=ReservationStatus.PENDIENTE, count=1),
            ReservationsByStatusItemDTO(status=ReservationStatus.CONFIRMADA, count=2),
            ReservationsByStatusItemDTO(status=ReservationStatus.CANCELADA, count=0),
            ReservationsByStatusItemDTO(status=ReservationStatus.COMPLETADA, count=0),
        ),
    )

    class StubUseCase:
        def execute(self, input_dto: object) -> ReservationsByStatusReportOutputDTO:
            return output

    app.dependency_overrides[get_get_reservations_by_status_report_use_case] = (
        StubUseCase
    )
    client = TestClient(app)

    response = client.get(
        "/reports/reservations-by-status?start_at=2026-07-01T10:00:00%2B00:00&end_at=2026-07-01T12:00:00%2B00:00"
    )

    assert response.status_code == 200
    assert response.json()["total_reservations"] == 3


def test_reports_return_422_on_invalid_range() -> None:
    app = create_app(enable_auth=False)
    client = TestClient(app)

    response = client.get(
        "/reports/revenue?start_at=2026-07-01T12:00:00%2B00:00&end_at=2026-07-01T10:00:00%2B00:00"
    )

    assert response.status_code == 422
