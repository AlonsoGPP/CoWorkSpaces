from uuid import UUID

from fastapi import APIRouter, Depends, status

from application.dto.space_dto import CreateSpaceInputDTO
from application.use_cases.create_space import CreateSpaceUseCase
from application.use_cases.get_space import GetSpaceUseCase
from application.use_cases.list_spaces import ListSpacesUseCase
from presentation.dependencies import (
    get_create_space_use_case,
    get_get_space_use_case,
    get_list_spaces_use_case,
)
from presentation.schemas.space import SpaceCreateRequest, SpaceResponse

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("", response_model=list[SpaceResponse])
def list_spaces(
    use_case: ListSpacesUseCase = Depends(get_list_spaces_use_case),
) -> list[SpaceResponse]:
    return [SpaceResponse.model_validate(item) for item in use_case.execute()]


@router.get("/{space_id}", response_model=SpaceResponse)
def get_space(
    space_id: UUID,
    use_case: GetSpaceUseCase = Depends(get_get_space_use_case),
) -> SpaceResponse:
    return SpaceResponse.model_validate(use_case.execute(space_id))


@router.post("", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_space(
    payload: SpaceCreateRequest,
    use_case: CreateSpaceUseCase = Depends(get_create_space_use_case),
) -> SpaceResponse:
    output = use_case.execute(
        CreateSpaceInputDTO(
            name=payload.name,
            status=payload.status,
            hourly_rate=payload.hourly_rate,
            capacity=payload.capacity,
        )
    )
    return SpaceResponse.model_validate(output)
