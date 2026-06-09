from uuid import uuid4

import pytest

from domain.exceptions import AuthenticationError
from infrastructure.security.jwt_token_service import JwtTokenService


def build_token_service() -> JwtTokenService:
    return JwtTokenService(
        secret_key="tests-secret-key-with-safe-length-123456",
        algorithm="HS256",
        access_token_ttl_seconds=3600,
        issuer="tests",
    )


def test_create_and_decode_access_token_roundtrip() -> None:
    token_service = build_token_service()
    user_id = uuid4()

    token = token_service.create_access_token(
        subject=str(user_id),
        additional_claims={"email": "admin@cowork.local"},
    )
    payload = token_service.decode_access_token(token)

    assert payload.subject == str(user_id)
    assert payload.email == "admin@cowork.local"


def test_decode_access_token_raises_for_invalid_token() -> None:
    token_service = build_token_service()

    with pytest.raises(AuthenticationError):
        token_service.decode_access_token("invalid-token")
