from decimal import ROUND_HALF_UP, Decimal

from application.dto.report_dto import (
    ReportRangeInputDTO,
    RevenueByRangeReportOutputDTO,
)
from application.interfaces.unit_of_work import UnitOfWork
from application.validators.report_range import validate_report_range


class GetRevenueByRangeReportUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, input_dto: ReportRangeInputDTO) -> RevenueByRangeReportOutputDTO:
        validate_report_range(start_at=input_dto.start_at, end_at=input_dto.end_at)

        with self._unit_of_work as uow:
            total_revenue = uow.reporting_repository.get_revenue_by_range(
                start_at=input_dto.start_at,
                end_at=input_dto.end_at,
            )

        return RevenueByRangeReportOutputDTO(
            start_at=input_dto.start_at,
            end_at=input_dto.end_at,
            total_revenue=Decimal(total_revenue).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            ),
        )
