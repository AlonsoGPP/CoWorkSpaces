from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from domain.enums import ReservationStatus
from domain.exceptions import ReservationNotCancelableError, ValidationError
from domain.services.cancellation_policy import CancellationPolicy


def test_full_refund_when_cancellation_is_more_than_48_hours() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=72)

    refund = policy.calculate_refund(
        total_amount=Decimal("200"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert refund == Decimal("200.00")


def test_half_refund_when_cancellation_is_between_24_and_48_hours() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=36)

    refund = policy.calculate_refund(
        total_amount=Decimal("200"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert refund == Decimal("100.00")


def test_half_refund_when_cancellation_is_exactly_24_hours() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=24)

    refund = policy.calculate_refund(
        total_amount=Decimal("200"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert refund == Decimal("100.00")


def test_no_refund_when_cancellation_is_less_than_24_hours() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=10)

    refund = policy.calculate_refund(
        total_amount=Decimal("200"),
        reservation_start_at=reservation_start_at,
        cancelled_at=cancelled_at,
        current_status=ReservationStatus.CONFIRMADA,
    )

    assert refund == Decimal("0.00")


def test_raises_when_reservation_is_completed() -> None:
    policy = CancellationPolicy()
    reservation_start_at = datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc)
    cancelled_at = reservation_start_at - timedelta(hours=72)

    with pytest.raises(ReservationNotCancelableError):
        policy.calculate_refund(
            total_amount=Decimal("200"),
            reservation_start_at=reservation_start_at,
            cancelled_at=cancelled_at,
            current_status=ReservationStatus.COMPLETADA,
        )


def test_raises_when_inputs_are_invalid() -> None:
    policy = CancellationPolicy()

    with pytest.raises(ValidationError):
        policy.calculate_refund(
            total_amount=Decimal("-1"),
            reservation_start_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
            cancelled_at=datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc),
            current_status=ReservationStatus.CONFIRMADA,
        )

    with pytest.raises(ValidationError):
        policy.calculate_refund(
            total_amount=Decimal("200"),
            reservation_start_at=datetime(2026, 6, 10, 10, 0),
            cancelled_at=datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc),
            current_status=ReservationStatus.CONFIRMADA,
        )
