from fastapi import APIRouter, Depends

from application.dto.auth_dto import LoginInputDTO
from application.use_cases.authenticate_user import AuthenticateUserUseCase
from presentation.dependencies import get_authenticate_user_use_case
from presentation.openapi import DEFAULT_ERROR_RESPONSES
from presentation.schemas.auth import AccessTokenResponse, LoginRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses=DEFAULT_ERROR_RESPONSES,
)


@router.post("/login", response_model=AccessTokenResponse)
def login(
    payload: LoginRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> AccessTokenResponse:
    output = use_case.execute(
        LoginInputDTO(
            email=payload.email,
            password=payload.password,
        )
    )
    return AccessTokenResponse.model_validate(output)
