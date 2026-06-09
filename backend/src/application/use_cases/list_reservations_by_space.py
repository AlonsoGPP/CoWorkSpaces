from uuid import UUID

from application.dto.reservation_dto import ReservationOutputDTO
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import EntityNotFoundError


class ListReservationsBySpaceUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, space_id: UUID) -> list[ReservationOutputDTO]:
        with self._unit_of_work as uow:
            space = uow.space_repository.get_by_id(space_id)
            if space is None:
                raise EntityNotFoundError("Espacio no encontrado")

            reservations = uow.reservation_repository.list_by_space(space_id)

        return [
            ReservationOutputDTO(
                id=reservation.id,
                space_id=reservation.space_id,
                start_at=reservation.reservation_window.start_at,
                end_at=reservation.reservation_window.end_at,
                status=reservation.status,
                total_price=reservation.total_price,
                created_at=reservation.created_at,
                cancelled_at=reservation.cancelled_at,
            )
            for reservation in reservations
        ]
