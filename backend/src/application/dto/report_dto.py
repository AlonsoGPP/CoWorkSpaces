from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.enums import ReservationStatus


@dataclass(frozen=True, slots=True)
class ReportRangeInputDTO:
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True, slots=True)
class OccupancyBySpaceRowDTO:
    space_id: UUID
    space_name: str
    occupied_minutes: Decimal
    reservations_count: int


@dataclass(frozen=True, slots=True)
class OccupancyBySpaceItemDTO:
    space_id: UUID
    space_name: str
    occupied_minutes: Decimal
    occupancy_percentage: Decimal
    reservations_count: int


@dataclass(frozen=True, slots=True)
class OccupancyBySpaceReportOutputDTO:
    start_at: datetime
    end_at: datetime
    total_minutes_in_range: Decimal
    items: tuple[OccupancyBySpaceItemDTO, ...]


@dataclass(frozen=True, slots=True)
class RevenueByRangeReportOutputDTO:
    start_at: datetime
    end_at: datetime
    total_revenue: Decimal


@dataclass(frozen=True, slots=True)
class ReservationsByStatusItemDTO:
    status: ReservationStatus
    count: int


@dataclass(frozen=True, slots=True)
class ReservationsByStatusReportOutputDTO:
    start_at: datetime
    end_at: datetime
    total_reservations: int
    items: tuple[ReservationsByStatusItemDTO, ...]
