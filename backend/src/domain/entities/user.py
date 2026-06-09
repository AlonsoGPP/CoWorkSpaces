from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.exceptions import ValidationError


@dataclass(slots=True)
class User:
    id: UUID
    email: str
    password_hash: str
    is_active: bool
    created_at: datetime

    def __post_init__(self) -> None:
        normalized_email = self.email.strip().lower()
        if "@" not in normalized_email:
            raise ValidationError("El correo electronico del usuario no es valido")
        if not self.password_hash.strip():
            raise ValidationError("El hash de contrasena no puede estar vacio")

        self.email = normalized_email
