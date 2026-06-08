import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from presentation.exception_handlers import register_exception_handlers
from presentation.routers.pricing import router as pricing_router
from presentation.routers.reports import router as reports_router
from presentation.routers.reservations import router as reservations_router
from presentation.routers.spaces import router as spaces_router


def _get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:4200")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title="CoWork Reservations API", version="0.1.0")
    register_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(spaces_router)
    app.include_router(reservations_router)
    app.include_router(pricing_router)
    app.include_router(reports_router)

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
