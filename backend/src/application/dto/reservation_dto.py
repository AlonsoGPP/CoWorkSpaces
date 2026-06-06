from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.enums import ReservationStatus


@dataclass(frozen=True, slots=True)
class CreateReservationInputDTO:
    space_id: UUID
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True, slots=True)
class CancelReservationInputDTO:
    reservation_id: UUID


@dataclass(frozen=True, slots=True)
class ReservationOutputDTO:
    id: UUID
    space_id: UUID
    start_at: datetime
    end_at: datetime
    status: ReservationStatus
    total_price: Decimal
    created_at: datetime
    cancelled_at: datetime | None


@dataclass(frozen=True, slots=True)
class CancelReservationOutputDTO:
    reservation: ReservationOutputDTO
    refund_amount: Decimal
