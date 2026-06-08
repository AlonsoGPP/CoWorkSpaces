from datetime import datetime
from decimal import Decimal
from typing import Protocol

from application.dto.report_dto import OccupancyBySpaceRowDTO
from domain.enums import ReservationStatus


class ReportingRepository(Protocol):
    def get_occupancy_by_space(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> list[OccupancyBySpaceRowDTO]: ...

    def get_revenue_by_range(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> Decimal: ...

    def get_reservations_count_by_status(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> dict[ReservationStatus, int]: ...
