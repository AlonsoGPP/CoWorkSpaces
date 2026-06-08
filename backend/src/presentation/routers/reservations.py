from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.dto.cancellation_dto import QuoteReservationCancellationInputDTO
from application.dto.reservation_dto import (
    CancelReservationInputDTO,
    CreateReservationInputDTO,
)
from application.use_cases.cancel_reservation import CancelReservationUseCase
from application.use_cases.create_reservation import CreateReservationUseCase
from application.use_cases.get_reservation import GetReservationUseCase
from application.use_cases.list_reservations_by_space import (
    ListReservationsBySpaceUseCase,
)
from application.use_cases.quote_reservation_cancellation import (
    QuoteReservationCancellationUseCase,
)
from presentation.dependencies import (
    get_cancel_reservation_use_case,
    get_create_reservation_use_case,
    get_get_reservation_use_case,
    get_list_reservations_by_space_use_case,
    get_quote_reservation_cancellation_use_case,
)
from presentation.openapi import DEFAULT_ERROR_RESPONSES
from presentation.schemas.reservation import (
    ReservationCancellationQuoteResponse,
    ReservationCancelResponse,
    ReservationCreateRequest,
    ReservationResponse,
)

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"],
    responses=DEFAULT_ERROR_RESPONSES,
)


@router.get("/by-space/{space_id}", response_model=list[ReservationResponse])
def list_reservations_by_space(
    space_id: UUID,
    use_case: ListReservationsBySpaceUseCase = Depends(
        get_list_reservations_by_space_use_case
    ),
) -> list[ReservationResponse]:
    output = use_case.execute(space_id)
    return [ReservationResponse.model_validate(item) for item in output]


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: UUID,
    use_case: GetReservationUseCase = Depends(get_get_reservation_use_case),
) -> ReservationResponse:
    output = use_case.execute(reservation_id)
    return ReservationResponse.model_validate(output)


@router.get(
    "/{reservation_id}/cancellation-quote",
    response_model=ReservationCancellationQuoteResponse,
)
def quote_reservation_cancellation(
    reservation_id: UUID,
    use_case: QuoteReservationCancellationUseCase = Depends(
        get_quote_reservation_cancellation_use_case
    ),
) -> ReservationCancellationQuoteResponse:
    output = use_case.execute(
        QuoteReservationCancellationInputDTO(reservation_id=reservation_id)
    )
    return ReservationCancellationQuoteResponse.model_validate(output)


@router.post(
    "",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(
    payload: ReservationCreateRequest,
    use_case: CreateReservationUseCase = Depends(get_create_reservation_use_case),
) -> ReservationResponse:
    output = use_case.execute(
        CreateReservationInputDTO(
            space_id=payload.space_id,
            start_at=payload.start_at,
            end_at=payload.end_at,
        )
    )
    return ReservationResponse.model_validate(output)


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationCancelResponse,
)
def cancel_reservation(
    reservation_id: UUID,
    use_case: CancelReservationUseCase = Depends(get_cancel_reservation_use_case),
) -> ReservationCancelResponse:
    output = use_case.execute(CancelReservationInputDTO(reservation_id=reservation_id))
    return ReservationCancelResponse.model_validate(output)
