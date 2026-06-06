from application.dto.reservation_dto import (
    CancelReservationInputDTO,
    CancelReservationOutputDTO,
    ReservationOutputDTO,
)
from application.interfaces.clock import Clock
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import EntityNotFoundError
from domain.services.cancellation_policy import CancellationPolicy


class CancelReservationUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        cancellation_policy: CancellationPolicy,
        clock: Clock,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._cancellation_policy = cancellation_policy
        self._clock = clock

    def execute(
        self,
        input_dto: CancelReservationInputDTO,
    ) -> CancelReservationOutputDTO:
        cancelled_at = self._clock.now()

        with self._unit_of_work as uow:
            reservation = uow.reservation_repository.get_by_id(input_dto.reservation_id)
            if reservation is None:
                raise EntityNotFoundError("Reserva no encontrada")

            refund_amount = self._cancellation_policy.calculate_refund(
                total_amount=reservation.total_price,
                reservation_start_at=reservation.reservation_window.start_at,
                cancelled_at=cancelled_at,
                current_status=reservation.status,
            )

            reservation.cancel(cancelled_at)
            updated = uow.reservation_repository.update(reservation)
            uow.commit()

        output_reservation = ReservationOutputDTO(
            id=updated.id,
            space_id=updated.space_id,
            start_at=updated.reservation_window.start_at,
            end_at=updated.reservation_window.end_at,
            status=updated.status,
            total_price=updated.total_price,
            created_at=updated.created_at,
            cancelled_at=updated.cancelled_at,
        )
        return CancelReservationOutputDTO(
            reservation=output_reservation,
            refund_amount=refund_amount,
        )
