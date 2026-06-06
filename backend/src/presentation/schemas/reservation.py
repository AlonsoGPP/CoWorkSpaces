from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.enums import ReservationStatus


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
