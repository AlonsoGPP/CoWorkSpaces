from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from threading import Lock
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.reservation_dto import (
    CreateReservationInputDTO,
    ReservationOutputDTO,
)
from domain.enums import ReservationStatus
from domain.exceptions import OverlappingReservationError
from presentation.api import create_app
from presentation.dependencies import get_create_reservation_use_case


class ConcurrentCreateReservationUseCase:
    def __init__(self) -> None:
        self._created = False
        self._lock = Lock()
        self.space_id = uuid4()
        self.reservation_id = uuid4()

    def execute(self, input_dto: CreateReservationInputDTO) -> ReservationOutputDTO:
        with self._lock:
            if self._created:
                raise OverlappingReservationError(
                    "Ya existe una reserva en ese rango para este espacio"
                )
            self._created = True

        return ReservationOutputDTO(
            id=self.reservation_id,
            space_id=input_dto.space_id,
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            status=ReservationStatus.CONFIRMADA,
            total_price=Decimal("200.00"),
            created_at=datetime.now(timezone.utc),
            cancelled_at=None,
        )


def test_concurrent_requests_return_201_and_409() -> None:
    app = create_app(enable_auth=False)
    use_case = ConcurrentCreateReservationUseCase()
    app.dependency_overrides[get_create_reservation_use_case] = lambda: use_case

    client = TestClient(app)

    payload = {
        "space_id": str(use_case.space_id),
        "start_at": "2026-06-15T10:00:00+00:00",
        "end_at": "2026-06-15T12:00:00+00:00",
    }

    def make_request() -> int:
        response = client.post("/reservations", json=payload)
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(lambda _: make_request(), range(2)))

    assert sorted(statuses) == [201, 409]
