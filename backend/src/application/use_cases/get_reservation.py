from uuid import UUID

from application.dto.reservation_dto import ReservationOutputDTO
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import EntityNotFoundError


class GetReservationUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, reservation_id: UUID) -> ReservationOutputDTO:
        with self._unit_of_work as uow:
            reservation = uow.reservation_repository.get_by_id(reservation_id)

        if reservation is None:
            raise EntityNotFoundError("Reserva no encontrada")

        return ReservationOutputDTO(
            id=reservation.id,
            space_id=reservation.space_id,
            start_at=reservation.reservation_window.start_at,
            end_at=reservation.reservation_window.end_at,
            status=reservation.status,
            total_price=reservation.total_price,
            created_at=reservation.created_at,
            cancelled_at=reservation.cancelled_at,
        )
