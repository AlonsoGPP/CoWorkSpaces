from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

from domain.enums import ReservationStatus
from domain.exceptions import ReservationNotCancelableError, ValidationError


@dataclass(frozen=True, slots=True)
class CancellationPolicyRules:
    full_refund_hours: int = 48
    half_refund_hours: int = 24


class RefundTier(str, Enum):
    COMPLETO = "COMPLETO"
    PARCIAL = "PARCIAL"
    SIN_REEMBOLSO = "SIN_REEMBOLSO"


@dataclass(frozen=True, slots=True)
class CancellationOutcome:
    refund_amount: Decimal
    refund_rate: Decimal
    tier: RefundTier


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
        outcome = self.calculate_outcome(
            total_amount=total_amount,
            reservation_start_at=reservation_start_at,
            cancelled_at=cancelled_at,
            current_status=current_status,
        )
        return outcome.refund_amount

    def calculate_outcome(
        self,
        *,
        total_amount: Decimal,
        reservation_start_at: datetime,
        cancelled_at: datetime,
        current_status: ReservationStatus,
    ) -> CancellationOutcome:
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
            refund_rate = Decimal("1")
            tier = RefundTier.COMPLETO
        elif remaining_time >= timedelta(hours=self._rules.half_refund_hours):
            refund_rate = Decimal("0.50")
            tier = RefundTier.PARCIAL
        else:
            refund_rate = Decimal("0")
            tier = RefundTier.SIN_REEMBOLSO

        refund_amount = (total_amount * refund_rate).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return CancellationOutcome(
            refund_amount=refund_amount,
            refund_rate=refund_rate,
            tier=tier,
        )
