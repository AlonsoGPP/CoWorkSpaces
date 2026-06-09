from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.entities.reservation import Reservation


class ReservationRepository(Protocol):
    def add(self, reservation: Reservation) -> Reservation: ...

    def get_by_id(self, reservation_id: UUID) -> Reservation | None: ...

    def list_by_space(self, space_id: UUID) -> list[Reservation]: ...

    def list_by_space_in_range(
        self,
        space_id: UUID,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Reservation]: ...

    def update(self, reservation: Reservation) -> Reservation: ...
