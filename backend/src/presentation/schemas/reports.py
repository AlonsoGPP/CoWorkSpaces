from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.enums import ReservationStatus


class ReportRangeQuery(BaseModel):
    start_at: datetime
    end_at: datetime


class OccupancyBySpaceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    space_id: UUID
    space_name: str
    occupied_minutes: Decimal
    occupancy_percentage: Decimal
    reservations_count: int


class OccupancyBySpaceReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_at: datetime
    end_at: datetime
    total_minutes_in_range: Decimal
    items: tuple[OccupancyBySpaceItemResponse, ...]


class RevenueByRangeReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_at: datetime
    end_at: datetime
    total_revenue: Decimal


class ReservationsByStatusItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: ReservationStatus
    count: int


class ReservationsByStatusReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_at: datetime
    end_at: datetime
    total_reservations: int
    items: tuple[ReservationsByStatusItemResponse, ...]
