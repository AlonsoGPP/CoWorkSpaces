from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.enums import ReservationStatus, SpaceStatus


@dataclass(frozen=True, slots=True)
class SpaceAvailabilityInputDTO:
    space_id: UUID
    start_at: datetime
    end_at: datetime
    slot_minutes: int = 30


@dataclass(frozen=True, slots=True)
class SpaceAvailabilityReservationItemDTO:
    reservation_id: UUID
    start_at: datetime
    end_at: datetime
    status: ReservationStatus
    total_price: Decimal
    blocks_availability: bool


@dataclass(frozen=True, slots=True)
class SpaceAvailabilitySlotItemDTO:
    start_at: datetime
    end_at: datetime
    is_available: bool
    overlapping_reservations_count: int


@dataclass(frozen=True, slots=True)
class SpaceAvailabilityOutputDTO:
    space_id: UUID
    space_name: str
    space_status: SpaceStatus
    start_at: datetime
    end_at: datetime
    slot_minutes: int
    total_slots: int
    available_slots: int
    availability_percentage: Decimal
    reservations: tuple[SpaceAvailabilityReservationItemDTO, ...]
    slots: tuple[SpaceAvailabilitySlotItemDTO, ...]
