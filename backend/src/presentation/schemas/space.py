from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.enums import SpaceStatus


class SpaceCreateRequest(BaseModel):
    name: str
    status: SpaceStatus = SpaceStatus.ACTIVO
    hourly_rate: Decimal
    capacity: int


class SpaceUpdateRequest(BaseModel):
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int


class SpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    status: SpaceStatus
    hourly_rate: Decimal
    capacity: int
