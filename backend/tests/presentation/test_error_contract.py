from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter
from fastapi.testclient import TestClient

from application.dto.space_dto import SpaceOutputDTO
from domain.exceptions import EntityNotFoundError
from presentation.api import create_app
from presentation.dependencies import get_get_space_use_case


def test_error_contract_for_not_found() -> None:
    app = create_app()

    class StubGetSpaceUseCase:
        def execute(self, space_id: object) -> SpaceOutputDTO:
            raise EntityNotFoundError("Espacio no encontrado")

    app.dependency_overrides[get_get_space_use_case] = StubGetSpaceUseCase
    client = TestClient(app)

    response = client.get(f"/spaces/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "not_found"
    assert response.json()["message"] == "Espacio no encontrado"


def test_error_contract_for_request_validation() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/spaces",
        json={
            "name": "",
            "status": "ACTIVO",
            "hourly_rate": "foo",
            "capacity": 3,
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "request_validation_error"
    assert response.json()["message"] == "La solicitud contiene datos invalidos"
    assert "details" in response.json()


def test_error_contract_for_internal_server_error() -> None:
    app = create_app()
    debug_router = APIRouter()

    @debug_router.get("/_debug/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    app.include_router(debug_router)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/_debug/boom")

    assert response.status_code == 500
    assert response.json()["error_code"] == "internal_server_error"
    assert response.json()["message"] == "Ocurrio un error interno del servidor"
