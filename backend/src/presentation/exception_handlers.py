from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import (
    DomainError,
    EntityNotFoundError,
    OverlappingReservationError,
    ReservationNotCancelableError,
    SpaceDeletionConflictError,
    SpaceUnavailableError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def handle_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(EntityNotFoundError)
    async def handle_not_found(
        request: Request,
        exc: EntityNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(OverlappingReservationError)
    async def handle_overlapping(
        request: Request,
        exc: OverlappingReservationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(SpaceUnavailableError)
    async def handle_space_unavailable(
        request: Request,
        exc: SpaceUnavailableError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(SpaceDeletionConflictError)
    async def handle_space_deletion_conflict(
        request: Request,
        exc: SpaceDeletionConflictError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ReservationNotCancelableError)
    async def handle_not_cancelable(
        request: Request,
        exc: ReservationNotCancelableError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
