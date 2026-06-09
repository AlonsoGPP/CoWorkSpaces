from uuid import UUID

from fastapi import APIRouter, Depends

from application.dto.availability_dto import SpaceAvailabilityInputDTO
from application.use_cases.get_space_availability import GetSpaceAvailabilityUseCase
from presentation.dependencies import get_get_space_availability_use_case
from presentation.openapi import DEFAULT_ERROR_RESPONSES
from presentation.schemas.availability import (
    SpaceAvailabilityQuery,
    SpaceAvailabilityResponse,
)

router = APIRouter(
    prefix="/availability",
    tags=["availability"],
    responses=DEFAULT_ERROR_RESPONSES,
)


@router.get("/by-space/{space_id}", response_model=SpaceAvailabilityResponse)
def get_space_availability(
    space_id: UUID,
    query: SpaceAvailabilityQuery = Depends(),
    use_case: GetSpaceAvailabilityUseCase = Depends(
        get_get_space_availability_use_case
    ),
) -> SpaceAvailabilityResponse:
    output = use_case.execute(
        SpaceAvailabilityInputDTO(
            space_id=space_id,
            start_at=query.start_at,
            end_at=query.end_at,
            slot_minutes=query.slot_minutes,
        )
    )
    return SpaceAvailabilityResponse.model_validate(output)
