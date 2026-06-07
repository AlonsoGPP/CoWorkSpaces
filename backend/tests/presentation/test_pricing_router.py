from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.pricing_dto import QuoteReservationPriceOutputDTO
from domain.exceptions import SpaceUnavailableError
from domain.services.pricing_engine import PricingRuleName
from presentation.api import create_app
from presentation.dependencies import get_quote_reservation_price_use_case


def _quote_output() -> QuoteReservationPriceOutputDTO:
    return QuoteReservationPriceOutputDTO(
        space_id=uuid4(),
        start_at=datetime(2026, 6, 13, 10, 0, tzinfo=timezone.utc),
        end_at=datetime(2026, 6, 13, 15, 0, tzinfo=timezone.utc),
        base_hourly_rate=Decimal("100.00"),
        total_price=Decimal("614.53"),
        applied_rules=(
            PricingRuleName.HORA_PICO,
            PricingRuleName.FIN_DE_SEMANA,
            PricingRuleName.RESERVA_LARGA,
            PricingRuleName.ANTICIPACION,
        ),
    )


def test_quote_pricing_returns_ok() -> None:
    app = create_app()
    quote_output = _quote_output()

    class StubQuoteReservationPriceUseCase:
        def execute(self, input_dto: object) -> QuoteReservationPriceOutputDTO:
            return quote_output

    app.dependency_overrides[get_quote_reservation_price_use_case] = (
        StubQuoteReservationPriceUseCase
    )
    client = TestClient(app)

    response = client.post(
        "/pricing/quote",
        json={
            "space_id": str(quote_output.space_id),
            "start_at": quote_output.start_at.isoformat(),
            "end_at": quote_output.end_at.isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.json()["total_price"] == "614.53"
    assert response.json()["applied_rules"] == [
        "HORA_PICO",
        "FIN_DE_SEMANA",
        "RESERVA_LARGA",
        "ANTICIPACION",
    ]


def test_quote_pricing_returns_conflict_for_maintenance_space() -> None:
    app = create_app()

    class StubQuoteReservationPriceUseCase:
        def execute(self, input_dto: object) -> QuoteReservationPriceOutputDTO:
            raise SpaceUnavailableError(
                "No se pueden cotizar reservas para espacios en mantenimiento"
            )

    app.dependency_overrides[get_quote_reservation_price_use_case] = (
        StubQuoteReservationPriceUseCase
    )
    client = TestClient(app)

    response = client.post(
        "/pricing/quote",
        json={
            "space_id": str(uuid4()),
            "start_at": "2026-06-13T10:00:00+00:00",
            "end_at": "2026-06-13T15:00:00+00:00",
        },
    )

    assert response.status_code == 409
