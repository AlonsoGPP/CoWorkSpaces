from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from domain.exceptions import ValidationError
from domain.value_objects.reservation_window import ReservationWindow


@dataclass(frozen=True, slots=True)
class PricingRules:
    peak_start_hour: int = 9
    peak_end_hour: int = 18
    long_reservation_minutes: int = 240
    early_booking_hours: int = 168

    peak_multiplier: Decimal = Decimal("1.25")
    weekend_multiplier: Decimal = Decimal("1.15")
    long_reservation_discount: Decimal = Decimal("0.10")
    early_booking_discount: Decimal = Decimal("0.05")


class PricingEngine:
    def __init__(self, rules: PricingRules | None = None) -> None:
        self._rules = rules or PricingRules()

    def calculate_total(
        self,
        *,
        base_hourly_rate: Decimal,
        reservation_window: ReservationWindow,
        booked_at: datetime,
    ) -> Decimal:
        if booked_at.tzinfo is None:
            raise ValidationError("booked_at debe incluir zona horaria")
        if base_hourly_rate <= Decimal("0"):
            raise ValidationError("La tarifa base debe ser mayor a cero")

        duration_hours = Decimal(str(reservation_window.duration_hours))
        total = base_hourly_rate * duration_hours

        # Orden obligatorio de reglas.
        if self._is_peak_hour(reservation_window):
            total *= self._rules.peak_multiplier

        if self._is_weekend(reservation_window):
            total *= self._rules.weekend_multiplier

        if reservation_window.duration >= timedelta(
            minutes=self._rules.long_reservation_minutes
        ):
            total *= Decimal("1") - self._rules.long_reservation_discount

        if reservation_window.start_at - booked_at >= timedelta(
            hours=self._rules.early_booking_hours
        ):
            total *= Decimal("1") - self._rules.early_booking_discount

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _is_peak_hour(self, reservation_window: ReservationWindow) -> bool:
        start_hour = reservation_window.start_at.hour
        return self._rules.peak_start_hour <= start_hour < self._rules.peak_end_hour

    def _is_weekend(self, reservation_window: ReservationWindow) -> bool:
        return reservation_window.start_at.weekday() >= 5
