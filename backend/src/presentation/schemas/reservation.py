from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.enums import ReservationStatus
from domain.services.cancellation_policy import RefundTier


class ReservationCreateRequest(BaseModel):
    space_id: UUID
    start_at: datetime
    end_at: datetime


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    start_at: datetime
    end_at: datetime
    status: ReservationStatus
    total_price: Decimal
    created_at: datetime
    cancelled_at: datetime | None


class ReservationCancelResponse(BaseModel):
    reservation: ReservationResponse
    refund_amount: Decimal


class ReservationCancellationQuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: UUID
    reservation_status: ReservationStatus
    reservation_start_at: datetime
    total_amount: Decimal
    refund_amount: Decimal
    refund_rate: Decimal
    refund_tier: RefundTier
    quoted_at: datetime
