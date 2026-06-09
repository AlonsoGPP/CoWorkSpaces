from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.space_dto import SpaceOutputDTO
from domain.enums import SpaceStatus
from domain.exceptions import EntityNotFoundError
from presentation.api import create_app
from presentation.dependencies import (
    get_create_space_use_case,
    get_delete_space_use_case,
    get_get_space_use_case,
    get_list_spaces_use_case,
    get_update_space_use_case,
)


def _space_output() -> SpaceOutputDTO:
    return SpaceOutputDTO(
        id=uuid4(),
        name="Sala Central",
        status=SpaceStatus.ACTIVO,
        hourly_rate=Decimal("150.00"),
        capacity=12,
    )


def test_list_spaces_returns_ok() -> None:
    app = create_app(enable_auth=False)

    class StubListSpacesUseCase:
        def execute(self) -> list[SpaceOutputDTO]:
            return [_space_output()]

    app.dependency_overrides[get_list_spaces_use_case] = StubListSpacesUseCase
    client = TestClient(app)

    response = client.get("/spaces")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_space_returns_ok() -> None:
    app = create_app(enable_auth=False)
    space_output = _space_output()

    class StubGetSpaceUseCase:
        def execute(self, space_id: object) -> SpaceOutputDTO:
            return space_output

    app.dependency_overrides[get_get_space_use_case] = StubGetSpaceUseCase
    client = TestClient(app)

    response = client.get(f"/spaces/{space_output.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(space_output.id)


def test_create_space_returns_created() -> None:
    app = create_app(enable_auth=False)
    space_output = _space_output()

    class StubCreateSpaceUseCase:
        def execute(self, input_dto: object) -> SpaceOutputDTO:
            return space_output

    app.dependency_overrides[get_create_space_use_case] = StubCreateSpaceUseCase
    client = TestClient(app)

    response = client.post(
        "/spaces",
        json={
            "name": "Sala Central",
            "status": "ACTIVO",
            "hourly_rate": "150.00",
            "capacity": 12,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Sala Central"


def test_update_space_returns_ok() -> None:
    app = create_app(enable_auth=False)
    space_output = _space_output()

    class StubUpdateSpaceUseCase:
        def execute(self, input_dto: object) -> SpaceOutputDTO:
            return space_output

    app.dependency_overrides[get_update_space_use_case] = StubUpdateSpaceUseCase
    client = TestClient(app)

    response = client.put(
        f"/spaces/{space_output.id}",
        json={
            "name": "Sala Central",
            "status": "ACTIVO",
            "hourly_rate": "150.00",
            "capacity": 12,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(space_output.id)


def test_update_space_returns_not_found() -> None:
    app = create_app(enable_auth=False)

    class StubUpdateSpaceUseCase:
        def execute(self, input_dto: object) -> SpaceOutputDTO:
            raise EntityNotFoundError("Espacio no encontrado")

    app.dependency_overrides[get_update_space_use_case] = StubUpdateSpaceUseCase
    client = TestClient(app)

    response = client.put(
        f"/spaces/{uuid4()}",
        json={
            "name": "Sala X",
            "status": "ACTIVO",
            "hourly_rate": "90.00",
            "capacity": 4,
        },
    )

    assert response.status_code == 404


def test_delete_space_returns_no_content() -> None:
    app = create_app(enable_auth=False)

    class StubDeleteSpaceUseCase:
        def execute(self, space_id: object) -> None:
            return None

    app.dependency_overrides[get_delete_space_use_case] = StubDeleteSpaceUseCase
    client = TestClient(app)

    response = client.delete(f"/spaces/{uuid4()}")

    assert response.status_code == 204
