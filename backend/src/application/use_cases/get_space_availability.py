from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from application.dto.availability_dto import (
    SpaceAvailabilityInputDTO,
    SpaceAvailabilityOutputDTO,
    SpaceAvailabilityReservationItemDTO,
    SpaceAvailabilitySlotItemDTO,
)
from application.interfaces.unit_of_work import UnitOfWork
from application.validators.availability import validate_slot_minutes
from application.validators.report_range import validate_report_range
from domain.enums import ReservationStatus
from domain.exceptions import EntityNotFoundError


_BLOCKING_STATUSES: frozenset[ReservationStatus] = frozenset(
    {ReservationStatus.PENDIENTE, ReservationStatus.CONFIRMADA}
)


class GetSpaceAvailabilityUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, input_dto: SpaceAvailabilityInputDTO) -> SpaceAvailabilityOutputDTO:
        validate_report_range(start_at=input_dto.start_at, end_at=input_dto.end_at)
        validate_slot_minutes(input_dto.slot_minutes)

        with self._unit_of_work as uow:
            space = uow.space_repository.get_by_id(input_dto.space_id)
            if space is None:
                raise EntityNotFoundError("Espacio no encontrado")

            reservations = uow.reservation_repository.list_by_space_in_range(
                input_dto.space_id,
                start_at=input_dto.start_at,
                end_at=input_dto.end_at,
            )

        reservation_items = tuple(
            SpaceAvailabilityReservationItemDTO(
                reservation_id=reservation.id,
                start_at=reservation.reservation_window.start_at,
                end_at=reservation.reservation_window.end_at,
                status=reservation.status,
                total_price=reservation.total_price,
                blocks_availability=reservation.status in _BLOCKING_STATUSES,
            )
            for reservation in reservations
        )

        slot_items = self._build_slot_items(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            slot_minutes=input_dto.slot_minutes,
            reservations=reservation_items,
        )
        total_slots = len(slot_items)
        available_slots = sum(1 for slot in slot_items if slot.is_available)

        if total_slots == 0:
            availability_percentage = Decimal("0.00")
        else:
            availability_percentage = (
                (Decimal(available_slots) / Decimal(total_slots)) * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return SpaceAvailabilityOutputDTO(
            space_id=space.id,
            space_name=space.name,
            space_status=space.status,
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            slot_minutes=input_dto.slot_minutes,
            total_slots=total_slots,
            available_slots=available_slots,
            availability_percentage=availability_percentage,
            reservations=reservation_items,
            slots=slot_items,
        )

    @staticmethod
    def _build_slot_items(
        *,
        start_at: datetime,
        end_at: datetime,
        slot_minutes: int,
        reservations: tuple[SpaceAvailabilityReservationItemDTO, ...],
    ) -> tuple[SpaceAvailabilitySlotItemDTO, ...]:
        slot_delta = timedelta(minutes=slot_minutes)
        blocking_reservations = tuple(
            reservation
            for reservation in reservations
            if reservation.blocks_availability
        )

        slots: list[SpaceAvailabilitySlotItemDTO] = []
        cursor = start_at

        while cursor < end_at:
            slot_end = min(cursor + slot_delta, end_at)

            overlapping_count = sum(
                1
                for reservation in blocking_reservations
                if reservation.start_at < slot_end and reservation.end_at > cursor
            )

            slots.append(
                SpaceAvailabilitySlotItemDTO(
                    start_at=cursor,
                    end_at=slot_end,
                    is_available=overlapping_count == 0,
                    overlapping_reservations_count=overlapping_count,
                )
            )
            cursor = slot_end

        return tuple(slots)
