from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from domain.exceptions import ValidationError
from domain.services.pricing_engine import PricingEngine
from domain.value_objects.reservation_window import ReservationWindow


def _window(start_at: datetime, hours: int) -> ReservationWindow:
    return ReservationWindow(
        start_at=start_at,
        end_at=start_at + timedelta(hours=hours),
    )


def test_calculate_total_base_only() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 8, 20, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 2),
        booked_at=booked_at,
    )

    assert total == Decimal("200.00")


def test_calculate_total_peak_hour_rule() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 9, 10, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 9, 8, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 2),
        booked_at=booked_at,
    )

    assert total == Decimal("250.00")


def test_calculate_total_weekend_rule() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 13, 20, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 13, 18, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 2),
        booked_at=booked_at,
    )

    assert total == Decimal("230.00")


def test_calculate_total_long_reservation_discount_rule() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 8, 20, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 8, 9, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 5),
        booked_at=booked_at,
    )

    assert total == Decimal("450.00")


def test_calculate_total_early_booking_discount_rule() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 16, 20, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 2),
        booked_at=booked_at,
    )

    assert total == Decimal("190.00")


def test_calculate_total_applies_rules_in_required_order() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc)

    total = engine.calculate_total(
        base_hourly_rate=Decimal("100"),
        reservation_window=_window(start_at, 5),
        booked_at=booked_at,
    )

    assert total == Decimal("614.53")


def test_calculate_total_raises_when_booked_at_is_naive() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 8, 20, 0, tzinfo=timezone.utc)

    with pytest.raises(ValidationError):
        engine.calculate_total(
            base_hourly_rate=Decimal("100"),
            reservation_window=_window(start_at, 2),
            booked_at=datetime(2026, 6, 8, 10, 0),
        )


def test_calculate_total_raises_when_base_rate_is_invalid() -> None:
    engine = PricingEngine()
    start_at = datetime(2026, 6, 8, 20, 0, tzinfo=timezone.utc)
    booked_at = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)

    with pytest.raises(ValidationError):
        engine.calculate_total(
            base_hourly_rate=Decimal("0"),
            reservation_window=_window(start_at, 2),
            booked_at=booked_at,
        )
