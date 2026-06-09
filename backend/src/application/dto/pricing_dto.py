from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.services.pricing_engine import PricingRuleName


@dataclass(frozen=True, slots=True)
class QuoteReservationPriceInputDTO:
    space_id: UUID
    start_at: datetime
    end_at: datetime


@dataclass(frozen=True, slots=True)
class QuoteReservationPriceOutputDTO:
    space_id: UUID
    start_at: datetime
    end_at: datetime
    base_hourly_rate: Decimal
    total_price: Decimal
    applied_rules: tuple[PricingRuleName, ...]
