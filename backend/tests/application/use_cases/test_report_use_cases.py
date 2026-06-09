from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Self
from uuid import uuid4

import pytest

from application.dto.report_dto import OccupancyBySpaceRowDTO, ReportRangeInputDTO
from application.use_cases.get_occupancy_by_space_report import (
    GetOccupancyBySpaceReportUseCase,
)
from application.use_cases.get_reservations_by_status_report import (
    GetReservationsByStatusReportUseCase,
)
from application.use_cases.get_revenue_by_range_report import (
    GetRevenueByRangeReportUseCase,
)
from domain.enums import ReservationStatus
from domain.exceptions import ValidationError


class FakeReportingRepository:
    def __init__(self) -> None:
        self.occupancy_rows: list[OccupancyBySpaceRowDTO] = []
        self.revenue: Decimal = Decimal("0")
        self.status_counts: dict[ReservationStatus, int] = {}

    def get_occupancy_by_space(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> list[OccupancyBySpaceRowDTO]:
        return self.occupancy_rows

    def get_revenue_by_range(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> Decimal:
        return self.revenue

    def get_reservations_count_by_status(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> dict[ReservationStatus, int]:
        return self.status_counts


@dataclass
class FakeUnitOfWork:
    reporting_repository: FakeReportingRepository

    @property
    def space_repository(self) -> None:
        return None

    @property
    def reservation_repository(self) -> None:
        return None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


def _range_input() -> ReportRangeInputDTO:
    return ReportRangeInputDTO(
        start_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
    )


def test_get_occupancy_by_space_report_happy_path() -> None:
    reporting_repository = FakeReportingRepository()
    reporting_repository.occupancy_rows = [
        OccupancyBySpaceRowDTO(
            space_id=uuid4(),
            space_name="Sala A",
            occupied_minutes=Decimal("60"),
            reservations_count=2,
        )
    ]
    use_case = GetOccupancyBySpaceReportUseCase(
        FakeUnitOfWork(reporting_repository=reporting_repository)
    )

    output = use_case.execute(_range_input())

    assert output.total_minutes_in_range == Decimal("120.00")
    assert len(output.items) == 1
    assert output.items[0].occupancy_percentage == Decimal("50.00")
    assert output.items[0].reservations_count == 2


def test_get_revenue_by_range_report_happy_path() -> None:
    reporting_repository = FakeReportingRepository()
    reporting_repository.revenue = Decimal("1234.5")
    use_case = GetRevenueByRangeReportUseCase(
        FakeUnitOfWork(reporting_repository=reporting_repository)
    )

    output = use_case.execute(_range_input())

    assert output.total_revenue == Decimal("1234.50")


def test_get_reservations_by_status_report_happy_path() -> None:
    reporting_repository = FakeReportingRepository()
    reporting_repository.status_counts = {
        ReservationStatus.CONFIRMADA: 3,
        ReservationStatus.CANCELADA: 1,
    }
    use_case = GetReservationsByStatusReportUseCase(
        FakeUnitOfWork(reporting_repository=reporting_repository)
    )

    output = use_case.execute(_range_input())

    assert output.total_reservations == 4
    counts = {item.status: item.count for item in output.items}
    assert counts[ReservationStatus.PENDIENTE] == 0
    assert counts[ReservationStatus.CONFIRMADA] == 3
    assert counts[ReservationStatus.CANCELADA] == 1
    assert counts[ReservationStatus.COMPLETADA] == 0


def test_reports_fail_when_range_is_invalid() -> None:
    invalid_range = ReportRangeInputDTO(
        start_at=datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
    )
    use_case = GetRevenueByRangeReportUseCase(
        FakeUnitOfWork(reporting_repository=FakeReportingRepository())
    )

    with pytest.raises(ValidationError):
        use_case.execute(invalid_range)
