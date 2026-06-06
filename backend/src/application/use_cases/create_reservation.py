from application.dto.reservation_dto import (
    CreateReservationInputDTO,
    ReservationOutputDTO,
)
from application.interfaces.clock import Clock
from application.interfaces.unit_of_work import UnitOfWork
from domain.entities.reservation import Reservation
from domain.enums import SpaceStatus
from domain.exceptions import EntityNotFoundError, SpaceUnavailableError
from domain.services.pricing_engine import PricingEngine
from domain.value_objects.reservation_window import ReservationWindow


class CreateReservationUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        pricing_engine: PricingEngine,
        clock: Clock,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._pricing_engine = pricing_engine
        self._clock = clock

    def execute(self, input_dto: CreateReservationInputDTO) -> ReservationOutputDTO:
        booked_at = self._clock.now()
        reservation_window = ReservationWindow(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
        )

        with self._unit_of_work as uow:
            space = uow.space_repository.get_by_id(input_dto.space_id)
            if space is None:
                raise EntityNotFoundError("Espacio no encontrado")
            if space.status == SpaceStatus.MANTENIMIENTO:
                raise SpaceUnavailableError(
                    "No se pueden crear reservas para espacios en mantenimiento"
                )

            total_price = self._pricing_engine.calculate_total(
                base_hourly_rate=space.hourly_rate,
                reservation_window=reservation_window,
                booked_at=booked_at,
            )

            reservation = Reservation.create(
                space_id=space.id,
                reservation_window=reservation_window,
                total_price=total_price,
            )

            created = uow.reservation_repository.add(reservation)
            uow.commit()

        return ReservationOutputDTO(
            id=created.id,
            space_id=created.space_id,
            start_at=created.reservation_window.start_at,
            end_at=created.reservation_window.end_at,
            status=created.status,
            total_price=created.total_price,
            created_at=created.created_at,
            cancelled_at=created.cancelled_at,
        )
