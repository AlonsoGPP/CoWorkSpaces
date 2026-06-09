from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.enums import ReservationStatus
from domain.services.cancellation_policy import RefundTier


@dataclass(frozen=True, slots=True)
class QuoteReservationCancellationInputDTO:
    reservation_id: UUID


@dataclass(frozen=True, slots=True)
class QuoteReservationCancellationOutputDTO:
    reservation_id: UUID
    reservation_status: ReservationStatus
    reservation_start_at: datetime
    total_amount: Decimal
    refund_amount: Decimal
    refund_rate: Decimal
    refund_tier: RefundTier
    quoted_at: datetime
