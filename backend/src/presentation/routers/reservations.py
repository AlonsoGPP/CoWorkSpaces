from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.dto.reservation_dto import (
    CancelReservationInputDTO,
    CreateReservationInputDTO,
)
from application.use_cases.cancel_reservation import CancelReservationUseCase
from application.use_cases.create_reservation import CreateReservationUseCase
from presentation.dependencies import (
    get_cancel_reservation_use_case,
    get_create_reservation_use_case,
)
from presentation.schemas.reservation import (
    ReservationCancelResponse,
    ReservationCreateRequest,
    ReservationResponse,
)

router = APIRouter(prefix="/reservations", tags=["reservations"])


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
