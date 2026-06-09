from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    EntityNotFoundError,
    InvalidCredentialsError,
    OverlappingReservationError,
    ReservationNotCancelableError,
    SpaceDeletionConflictError,
    SpaceUnavailableError,
    ValidationError,
)
from presentation.schemas.common import ErrorResponse


def _build_error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: tuple[str, ...] | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(
        request: Request,
        exc: InvalidCredentialsError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=401,
            error_code="invalid_credentials",
            message=str(exc),
        )

    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(
        request: Request,
        exc: AuthenticationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=401,
            error_code="authentication_error",
            message=str(exc),
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(
        request: Request,
        exc: AuthorizationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=403,
            error_code="forbidden",
            message=str(exc),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = tuple(
            (
                f"{'.'.join(str(item) for item in error.get('loc', ()))}: "
                f"{error.get('msg', '')}"
            )
            for error in exc.errors()
        )
        return _build_error_response(
            status_code=422,
            error_code="request_validation_error",
            message="La solicitud contiene datos invalidos",
            details=details,
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=exc.status_code,
            error_code="http_error",
            message=str(exc.detail),
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=422,
            error_code="validation_error",
            message=str(exc),
        )

    @app.exception_handler(EntityNotFoundError)
    async def handle_not_found(
        request: Request,
        exc: EntityNotFoundError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=404,
            error_code="not_found",
            message=str(exc),
        )

    @app.exception_handler(OverlappingReservationError)
    async def handle_overlapping(
        request: Request,
        exc: OverlappingReservationError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=409,
            error_code="reservation_overlap",
            message=str(exc),
        )

    @app.exception_handler(SpaceUnavailableError)
    async def handle_space_unavailable(
        request: Request,
        exc: SpaceUnavailableError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=409,
            error_code="space_unavailable",
            message=str(exc),
        )

    @app.exception_handler(SpaceDeletionConflictError)
    async def handle_space_deletion_conflict(
        request: Request,
        exc: SpaceDeletionConflictError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=409,
            error_code="space_deletion_conflict",
            message=str(exc),
        )

    @app.exception_handler(ReservationNotCancelableError)
    async def handle_not_cancelable(
        request: Request,
        exc: ReservationNotCancelableError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=409,
            error_code="reservation_not_cancelable",
            message=str(exc),
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=400,
            error_code="domain_error",
            message=str(exc),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return _build_error_response(
            status_code=500,
            error_code="internal_server_error",
            message="Ocurrio un error interno del servidor",
        )
