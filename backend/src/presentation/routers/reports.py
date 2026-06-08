from fastapi import APIRouter, Depends

from application.dto.report_dto import ReportRangeInputDTO
from application.use_cases.get_occupancy_by_space_report import (
    GetOccupancyBySpaceReportUseCase,
)
from application.use_cases.get_reservations_by_status_report import (
    GetReservationsByStatusReportUseCase,
)
from application.use_cases.get_revenue_by_range_report import (
    GetRevenueByRangeReportUseCase,
)
from presentation.dependencies import (
    get_get_occupancy_by_space_report_use_case,
    get_get_reservations_by_status_report_use_case,
    get_get_revenue_by_range_report_use_case,
)
from presentation.openapi import DEFAULT_ERROR_RESPONSES
from presentation.schemas.reports import (
    OccupancyBySpaceReportResponse,
    ReportRangeQuery,
    ReservationsByStatusReportResponse,
    RevenueByRangeReportResponse,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses=DEFAULT_ERROR_RESPONSES,
)


@router.get("/occupancy-by-space", response_model=OccupancyBySpaceReportResponse)
def get_occupancy_by_space_report(
    query: ReportRangeQuery = Depends(),
    use_case: GetOccupancyBySpaceReportUseCase = Depends(
        get_get_occupancy_by_space_report_use_case
    ),
) -> OccupancyBySpaceReportResponse:
    output = use_case.execute(
        ReportRangeInputDTO(start_at=query.start_at, end_at=query.end_at)
    )
    return OccupancyBySpaceReportResponse.model_validate(output)


@router.get("/revenue", response_model=RevenueByRangeReportResponse)
def get_revenue_by_range_report(
    query: ReportRangeQuery = Depends(),
    use_case: GetRevenueByRangeReportUseCase = Depends(
        get_get_revenue_by_range_report_use_case
    ),
) -> RevenueByRangeReportResponse:
    output = use_case.execute(
        ReportRangeInputDTO(start_at=query.start_at, end_at=query.end_at)
    )
    return RevenueByRangeReportResponse.model_validate(output)


@router.get(
    "/reservations-by-status",
    response_model=ReservationsByStatusReportResponse,
)
def get_reservations_by_status_report(
    query: ReportRangeQuery = Depends(),
    use_case: GetReservationsByStatusReportUseCase = Depends(
        get_get_reservations_by_status_report_use_case
    ),
) -> ReservationsByStatusReportResponse:
    output = use_case.execute(
        ReportRangeInputDTO(start_at=query.start_at, end_at=query.end_at)
    )
    return ReservationsByStatusReportResponse.model_validate(output)
