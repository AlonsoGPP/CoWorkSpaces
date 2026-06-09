from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from application.dto.auth_dto import AccessTokenPayloadDTO
from application.interfaces.token_service import TokenService
from domain.exceptions import AuthenticationError


class JwtTokenService(TokenService):
    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str,
        access_token_ttl_seconds: int,
        issuer: str,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_ttl_seconds = access_token_ttl_seconds
        self._issuer = issuer

    def create_access_token(
        self,
        *,
        subject: str,
        additional_claims: dict[str, str] | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self._access_token_ttl_seconds)

        payload: dict[str, str | int] = {
            "sub": subject,
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }
        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> AccessTokenPayloadDTO:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                options={"require": ["sub", "exp", "iat", "iss"]},
            )
        except InvalidTokenError as error:
            raise AuthenticationError("Token invalido o expirado") from error

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise AuthenticationError("Token invalido o expirado")

        email_claim = payload.get("email")
        email = email_claim if isinstance(email_claim, str) else None
        return AccessTokenPayloadDTO(subject=subject, email=email)

    @property
    def access_token_ttl_seconds(self) -> int:
        return self._access_token_ttl_seconds
