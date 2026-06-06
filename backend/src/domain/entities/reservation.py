from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from domain.enums import ReservationStatus
from domain.exceptions import ReservationNotCancelableError, ValidationError
from domain.value_objects.reservation_window import ReservationWindow


@dataclass(slots=True)
class Reservation:
    id: UUID
    space_id: UUID
    reservation_window: ReservationWindow
    status: ReservationStatus
    total_price: Decimal
    created_at: datetime
    cancelled_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        space_id: UUID,
        reservation_window: ReservationWindow,
        total_price: Decimal,
        status: ReservationStatus = ReservationStatus.CONFIRMADA,
    ) -> "Reservation":
        return cls(
            id=uuid4(),
            space_id=space_id,
            reservation_window=reservation_window,
            status=status,
            total_price=total_price,
            created_at=datetime.now(timezone.utc),
        )

    def __post_init__(self) -> None:
        if self.total_price < Decimal("0"):
            raise ValidationError("El precio total no puede ser negativo")

    def cancel(self, cancelled_at: datetime) -> None:
        if self.status == ReservationStatus.COMPLETADA:
            raise ReservationNotCancelableError(
                "No se puede cancelar una reserva completada"
            )
        if self.status == ReservationStatus.CANCELADA:
            raise ReservationNotCancelableError("La reserva ya se encuentra cancelada")

        self.status = ReservationStatus.CANCELADA
        self.cancelled_at = cancelled_at
