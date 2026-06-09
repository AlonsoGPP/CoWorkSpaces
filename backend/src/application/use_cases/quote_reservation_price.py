from application.dto.pricing_dto import (
    QuoteReservationPriceInputDTO,
    QuoteReservationPriceOutputDTO,
)
from application.interfaces.clock import Clock
from application.interfaces.unit_of_work import UnitOfWork
from domain.enums import SpaceStatus
from domain.exceptions import EntityNotFoundError, SpaceUnavailableError
from domain.services.pricing_engine import PricingEngine
from domain.value_objects.reservation_window import ReservationWindow


class QuoteReservationPriceUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        pricing_engine: PricingEngine,
        clock: Clock,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._pricing_engine = pricing_engine
        self._clock = clock

    def execute(
        self,
        input_dto: QuoteReservationPriceInputDTO,
    ) -> QuoteReservationPriceOutputDTO:
        reservation_window = ReservationWindow(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
        )
        booked_at = self._clock.now()

        with self._unit_of_work as uow:
            space = uow.space_repository.get_by_id(input_dto.space_id)
            if space is None:
                raise EntityNotFoundError("Espacio no encontrado")
            if space.status == SpaceStatus.MANTENIMIENTO:
                raise SpaceUnavailableError(
                    "No se pueden cotizar reservas para espacios en mantenimiento"
                )

        breakdown = self._pricing_engine.calculate_breakdown(
            base_hourly_rate=space.hourly_rate,
            reservation_window=reservation_window,
            booked_at=booked_at,
        )

        return QuoteReservationPriceOutputDTO(
            space_id=space.id,
            start_at=reservation_window.start_at,
            end_at=reservation_window.end_at,
            base_hourly_rate=space.hourly_rate,
            total_price=breakdown.total,
            applied_rules=breakdown.applied_rules,
        )
