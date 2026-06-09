from application.dto.report_dto import (
    ReportRangeInputDTO,
    ReservationsByStatusItemDTO,
    ReservationsByStatusReportOutputDTO,
)
from application.interfaces.unit_of_work import UnitOfWork
from application.validators.report_range import validate_report_range
from domain.enums import ReservationStatus


class GetReservationsByStatusReportUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self,
        input_dto: ReportRangeInputDTO,
    ) -> ReservationsByStatusReportOutputDTO:
        validate_report_range(start_at=input_dto.start_at, end_at=input_dto.end_at)

        with self._unit_of_work as uow:
            counts = uow.reporting_repository.get_reservations_count_by_status(
                start_at=input_dto.start_at,
                end_at=input_dto.end_at,
            )

        items = tuple(
            ReservationsByStatusItemDTO(status=status, count=counts.get(status, 0))
            for status in ReservationStatus
        )
        total_reservations = sum(item.count for item in items)

        return ReservationsByStatusReportOutputDTO(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            total_reservations=total_reservations,
            items=items,
        )
