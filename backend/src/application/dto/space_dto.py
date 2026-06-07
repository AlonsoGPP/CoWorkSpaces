from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.enums import SpaceStatus


@dataclass(frozen=True, slots=True)
class CreateSpaceInputDTO:
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int


@dataclass(frozen=True, slots=True)
class UpdateSpaceInputDTO:
    space_id: UUID
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int


@dataclass(frozen=True, slots=True)
class SpaceOutputDTO:
    id: UUID
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int
