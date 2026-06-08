from datetime import datetime, timedelta, timezone
from decimal import Decimal

from domain.enums import ReservationStatus
from domain.services.cancellation_policy import CancellationPolicy, RefundTier


def test_calculate_outcome_returns_full_refund_tier() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=72)

    outcome = policy.calculate_outcome(
        total_amount=Decimal("300"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert outcome.refund_amount == Decimal("300.00")
    assert outcome.refund_rate == Decimal("1")
    assert outcome.tier == RefundTier.COMPLETO


def test_calculate_outcome_returns_partial_refund_tier() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=30)

    outcome = policy.calculate_outcome(
        total_amount=Decimal("300"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert outcome.refund_amount == Decimal("150.00")
    assert outcome.refund_rate == Decimal("0.50")
    assert outcome.tier == RefundTier.PARCIAL


def test_calculate_outcome_returns_no_refund_tier() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=5)

    outcome = policy.calculate_outcome(
        total_amount=Decimal("300"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert outcome.refund_amount == Decimal("0.00")
    assert outcome.refund_rate == Decimal("0")
    assert outcome.tier == RefundTier.SIN_REEMBOLSO
