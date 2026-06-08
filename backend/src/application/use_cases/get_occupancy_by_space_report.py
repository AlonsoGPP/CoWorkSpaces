from decimal import ROUND_HALF_UP, Decimal

from application.dto.report_dto import (
    OccupancyBySpaceItemDTO,
    OccupancyBySpaceReportOutputDTO,
    ReportRangeInputDTO,
)
from application.interfaces.unit_of_work import UnitOfWork
from application.validators.report_range import validate_report_range


class GetOccupancyBySpaceReportUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self, input_dto: ReportRangeInputDTO
    ) -> OccupancyBySpaceReportOutputDTO:
        validate_report_range(start_at=input_dto.start_at, end_at=input_dto.end_at)

        total_minutes_in_range = Decimal(
            (input_dto.end_at - input_dto.start_at).total_seconds()
        ) / Decimal("60")

        with self._unit_of_work as uow:
            rows = uow.reporting_repository.get_occupancy_by_space(
                start_at=input_dto.start_at,
                end_at=input_dto.end_at,
            )

        items: list[OccupancyBySpaceItemDTO] = []
        for row in rows:
            if total_minutes_in_range == Decimal("0"):
                occupancy_percentage = Decimal("0")
            else:
                occupancy_percentage = (
                    row.occupied_minutes / total_minutes_in_range
                ) * Decimal("100")

            items.append(
                OccupancyBySpaceItemDTO(
                    space_id=row.space_id,
                    space_name=row.space_name,
                    occupied_minutes=row.occupied_minutes.quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP,
                    ),
                    occupancy_percentage=occupancy_percentage.quantize(
                        Decimal("0.01"),
                        rounding=ROUND_HALF_UP,
                    ),
                    reservations_count=row.reservations_count,
                )
            )

        return OccupancyBySpaceReportOutputDTO(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            total_minutes_in_range=total_minutes_in_range.quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            ),
            items=tuple(items),
        )
