from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from domain.enums import ReservationStatus, SpaceStatus


class SpaceAvailabilityQuery(BaseModel):
    start_at: datetime
    end_at: datetime
    slot_minutes: int = Field(default=30, ge=15, le=120, multiple_of=5)


class SpaceAvailabilityReservationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: UUID
    start_at: datetime
    end_at: datetime
    status: ReservationStatus
    total_price: Decimal
    blocks_availability: bool


class SpaceAvailabilitySlotItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    start_at: datetime
    end_at: datetime
    is_available: bool
    overlapping_reservations_count: int


class SpaceAvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    space_id: UUID
    space_name: str
    space_status: SpaceStatus
    start_at: datetime
    end_at: datetime
    slot_minutes: int
    total_slots: int
    available_slots: int
    availability_percentage: Decimal
    reservations: tuple[SpaceAvailabilityReservationItemResponse, ...]
    slots: tuple[SpaceAvailabilitySlotItemResponse, ...]
