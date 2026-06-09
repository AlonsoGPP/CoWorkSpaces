from application.dto.cancellation_dto import (
    QuoteReservationCancellationInputDTO,
    QuoteReservationCancellationOutputDTO,
)
from application.interfaces.clock import Clock
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import EntityNotFoundError
from domain.services.cancellation_policy import CancellationPolicy


class QuoteReservationCancellationUseCase:
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
        input_dto: QuoteReservationCancellationInputDTO,
    ) -> QuoteReservationCancellationOutputDTO:
        quoted_at = self._clock.now()

        with self._unit_of_work as uow:
            reservation = uow.reservation_repository.get_by_id(input_dto.reservation_id)
            if reservation is None:
                raise EntityNotFoundError("Reserva no encontrada")

        outcome = self._cancellation_policy.calculate_outcome(
            total_amount=reservation.total_price,
            reservation_start_at=reservation.reservation_window.start_at,
            cancelled_at=quoted_at,
            current_status=reservation.status,
        )

        return QuoteReservationCancellationOutputDTO(
            reservation_id=reservation.id,
            reservation_status=reservation.status,
            reservation_start_at=reservation.reservation_window.start_at,
            total_amount=reservation.total_price,
            refund_amount=outcome.refund_amount,
            refund_rate=outcome.refund_rate,
            refund_tier=outcome.tier,
            quoted_at=quoted_at,
        )
