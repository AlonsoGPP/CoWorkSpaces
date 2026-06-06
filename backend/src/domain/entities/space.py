from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.enums import SpaceStatus
from domain.exceptions import ValidationError


@dataclass(slots=True)
class Space:
    id: UUID
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValidationError("El nombre del espacio es obligatorio")
        if self.hourly_rate <= Decimal("0"):
            raise ValidationError("La tarifa por hora debe ser mayor a cero")
        if self.capacity <= 0:
            raise ValidationError("La capacidad debe ser mayor a cero")
