from typing import Protocol
from uuid import UUID

from domain.entities.space import Space


class SpaceRepository(Protocol):
    def get_by_id(self, space_id: UUID) -> Space | None: ...

    def list_all(self) -> list[Space]: ...

    def add(self, space: Space) -> Space: ...

    def update(self, space: Space) -> Space: ...
