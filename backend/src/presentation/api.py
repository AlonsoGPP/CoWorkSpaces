from fastapi import FastAPI

from presentation.exception_handlers import register_exception_handlers
from presentation.routers.reservations import router as reservations_router
from presentation.routers.spaces import router as spaces_router


def create_app() -> FastAPI:
    app = FastAPI(title="CoWork Reservations API", version="0.1.0")
    register_exception_handlers(app)

    app.include_router(spaces_router)
    app.include_router(reservations_router)

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
