from typing import Protocol

from application.dto.auth_dto import AccessTokenPayloadDTO


class TokenService(Protocol):
    def create_access_token(
        self,
        *,
        subject: str,
        additional_claims: dict[str, str] | None = None,
    ) -> str: ...

    def decode_access_token(self, token: str) -> AccessTokenPayloadDTO: ...
