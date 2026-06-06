from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from domain.enums import ReservationStatus
from domain.exceptions import ReservationNotCancelableError, ValidationError


@dataclass(frozen=True, slots=True)
class CancellationPolicyRules:
    full_refund_hours: int = 48
    half_refund_hours: int = 24


class CancellationPolicy:
    def __init__(self, rules: CancellationPolicyRules | None = None) -> None:
        self._rules = rules or CancellationPolicyRules()

    def calculate_refund(
        self,
        *,
        total_amount: Decimal,
        reservation_start_at: datetime,
        cancelled_at: datetime,
        current_status: ReservationStatus,
    ) -> Decimal:
        if reservation_start_at.tzinfo is None or cancelled_at.tzinfo is None:
            raise ValidationError("Las fechas deben incluir zona horaria")
        if total_amount < Decimal("0"):
            raise ValidationError("El monto total no puede ser negativo")
        if current_status == ReservationStatus.COMPLETADA:
            raise ReservationNotCancelableError(
                "No se puede cancelar una reserva completada"
            )

        remaining_time = reservation_start_at - cancelled_at

        if remaining_time > timedelta(hours=self._rules.full_refund_hours):
            refund = total_amount
        elif remaining_time >= timedelta(hours=self._rules.half_refund_hours):
            refund = total_amount * Decimal("0.50")
        else:
            refund = Decimal("0")

        return refund.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
