from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.cancellation_dto import QuoteReservationCancellationOutputDTO
from domain.enums import ReservationStatus
from domain.exceptions import EntityNotFoundError, ReservationNotCancelableError
from domain.services.cancellation_policy import RefundTier
from presentation.api import create_app
from presentation.dependencies import get_quote_reservation_cancellation_use_case


def _quote_output() -> QuoteReservationCancellationOutputDTO:
    return QuoteReservationCancellationOutputDTO(
        reservation_id=uuid4(),
        reservation_status=ReservationStatus.CONFIRMADA,
        reservation_start_at=datetime(2026, 7, 10, 10, 0, tzinfo=timezone.utc),
        total_amount=Decimal("200.00"),
        refund_amount=Decimal("100.00"),
        refund_rate=Decimal("0.50"),
        refund_tier=RefundTier.PARCIAL,
        quoted_at=datetime(2026, 7, 9, 10, 0, tzinfo=timezone.utc),
    )


def test_quote_cancellation_returns_ok() -> None:
    app = create_app(enable_auth=False)
    quote_output = _quote_output()

    class StubQuoteReservationCancellationUseCase:
        def execute(
            self,
            input_dto: object,
        ) -> QuoteReservationCancellationOutputDTO:
            return quote_output

    app.dependency_overrides[get_quote_reservation_cancellation_use_case] = (
        StubQuoteReservationCancellationUseCase
    )
    client = TestClient(app)

    response = client.get(
        f"/reservations/{quote_output.reservation_id}/cancellation-quote"
    )

    assert response.status_code == 200
    assert response.json()["refund_amount"] == "100.00"
    assert response.json()["refund_tier"] == "PARCIAL"


def test_quote_cancellation_returns_not_found() -> None:
    app = create_app(enable_auth=False)

    class StubQuoteReservationCancellationUseCase:
        def execute(
            self,
            input_dto: object,
        ) -> QuoteReservationCancellationOutputDTO:
            raise EntityNotFoundError("Reserva no encontrada")

    app.dependency_overrides[get_quote_reservation_cancellation_use_case] = (
        StubQuoteReservationCancellationUseCase
    )
    client = TestClient(app)

    response = client.get(f"/reservations/{uuid4()}/cancellation-quote")

    assert response.status_code == 404


def test_quote_cancellation_returns_conflict_when_completed() -> None:
    app = create_app(enable_auth=False)

    class StubQuoteReservationCancellationUseCase:
        def execute(
            self,
            input_dto: object,
        ) -> QuoteReservationCancellationOutputDTO:
            raise ReservationNotCancelableError(
                "No se puede cancelar una reserva completada"
            )

    app.dependency_overrides[get_quote_reservation_cancellation_use_case] = (
        StubQuoteReservationCancellationUseCase
    )
    client = TestClient(app)

    response = client.get(f"/reservations/{uuid4()}/cancellation-quote")

    assert response.status_code == 409
