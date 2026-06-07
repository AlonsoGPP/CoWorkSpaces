from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.services.pricing_engine import PricingRuleName


class PricingQuoteRequest(BaseModel):
    space_id: UUID
    start_at: datetime
    end_at: datetime


class PricingQuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    space_id: UUID
    start_at: datetime
    end_at: datetime
    base_hourly_rate: Decimal
    total_price: Decimal
    applied_rules: tuple[PricingRuleName, ...]
