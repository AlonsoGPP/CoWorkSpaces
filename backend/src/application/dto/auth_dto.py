from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class LoginInputDTO:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class AuthTokenOutputDTO:
    access_token: str
    token_type: str
    expires_in_seconds: int


@dataclass(frozen=True, slots=True)
class AuthenticatedUserDTO:
    user_id: UUID
    email: str


@dataclass(frozen=True, slots=True)
class AccessTokenPayloadDTO:
    subject: str
    email: str | None
