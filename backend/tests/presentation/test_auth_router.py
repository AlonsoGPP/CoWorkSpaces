from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from application.dto.auth_dto import AuthenticatedUserDTO, AuthTokenOutputDTO
from domain.exceptions import InvalidCredentialsError
from presentation.api import create_app
from presentation.dependencies import (
    get_authenticate_user_use_case,
    get_list_spaces_use_case,
    require_authenticated_user,
)


def test_login_returns_access_token() -> None:
    app = create_app(enable_auth=True)

    class StubAuthenticateUserUseCase:
        def execute(self, input_dto: object) -> AuthTokenOutputDTO:
            return AuthTokenOutputDTO(
                access_token="jwt-token",
                token_type="bearer",
                expires_in_seconds=3600,
            )

    app.dependency_overrides[get_authenticate_user_use_case] = (
        StubAuthenticateUserUseCase
    )
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"email": "admin@cowork.local", "password": "Admin123!"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "jwt-token"
    assert response.json()["token_type"] == "bearer"


def test_login_returns_401_when_credentials_are_invalid() -> None:
    app = create_app(enable_auth=True)

    class StubAuthenticateUserUseCase:
        def execute(self, input_dto: object) -> AuthTokenOutputDTO:
            raise InvalidCredentialsError("Credenciales invalidas")

    app.dependency_overrides[get_authenticate_user_use_case] = (
        StubAuthenticateUserUseCase
    )
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"email": "admin@cowork.local", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "invalid_credentials"


def test_protected_endpoint_requires_token() -> None:
    app = create_app(enable_auth=True)
    client = TestClient(app)

    response = client.get("/spaces")

    assert response.status_code == 401
    assert response.json()["error_code"] == "authentication_error"


def test_protected_endpoint_returns_ok_with_authenticated_override() -> None:
    app = create_app(enable_auth=True)

    class StubListSpacesUseCase:
        def execute(self) -> list[object]:
            return []

    def stub_require_authenticated_user() -> AuthenticatedUserDTO:
        return AuthenticatedUserDTO(
            user_id=uuid4(),
            email="admin@cowork.local",
        )

    app.dependency_overrides[require_authenticated_user] = (
        stub_require_authenticated_user
    )
    app.dependency_overrides[get_list_spaces_use_case] = StubListSpacesUseCase
    client = TestClient(app)

    response = client.get("/spaces", headers={"Authorization": "Bearer any-token"})

    assert response.status_code == 200
    assert response.json() == []
