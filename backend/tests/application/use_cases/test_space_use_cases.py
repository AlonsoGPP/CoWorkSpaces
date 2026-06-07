from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

import pytest

from application.dto.space_dto import CreateSpaceInputDTO, UpdateSpaceInputDTO
from application.use_cases.create_space import CreateSpaceUseCase
from application.use_cases.delete_space import DeleteSpaceUseCase
from application.use_cases.update_space import UpdateSpaceUseCase
from domain.entities.space import Space
from domain.enums import SpaceStatus
from domain.exceptions import EntityNotFoundError


class FakeSpaceRepository:
    def __init__(self, spaces: list[Space] | None = None) -> None:
        self._spaces = {space.id: space for space in spaces or []}

    def get_by_id(self, space_id: UUID) -> Space | None:
        return self._spaces.get(space_id)

    def list_all(self) -> list[Space]:
        return list(self._spaces.values())

    def add(self, space: Space) -> Space:
        self._spaces[space.id] = space
        return space

    def update(self, space: Space) -> Space:
        if space.id not in self._spaces:
            raise EntityNotFoundError("Espacio no encontrado")
        self._spaces[space.id] = space
        return space

    def delete(self, space_id: UUID) -> None:
        if space_id not in self._spaces:
            raise EntityNotFoundError("Espacio no encontrado")
        del self._spaces[space_id]


@dataclass
class FakeUnitOfWork:
    space_repository: FakeSpaceRepository
    committed: bool = False

    @property
    def reservation_repository(self) -> None:
        return None

    def __enter__(self) -> Self:
        self.committed = False
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


def _space() -> Space:
    return Space(
        id=uuid4(),
        name="Sala Norte",
        status=SpaceStatus.ACTIVO,
        hourly_rate=Decimal("120"),
        capacity=8,
    )


def test_create_space_happy_path() -> None:
    uow = FakeUnitOfWork(space_repository=FakeSpaceRepository())
    use_case = CreateSpaceUseCase(uow)

    output = use_case.execute(
        CreateSpaceInputDTO(
            name="Sala Sur",
            status=SpaceStatus.ACTIVO,
            hourly_rate=Decimal("100"),
            capacity=4,
        )
    )

    assert output.name == "Sala Sur"
    assert output.status == SpaceStatus.ACTIVO
    assert output.hourly_rate == Decimal("100")
    assert output.capacity == 4
    assert uow.committed is True


def test_update_space_happy_path() -> None:
    existing = _space()
    uow = FakeUnitOfWork(space_repository=FakeSpaceRepository([existing]))
    use_case = UpdateSpaceUseCase(uow)

    output = use_case.execute(
        UpdateSpaceInputDTO(
            space_id=existing.id,
            name="Sala Norte Renovada",
            status=SpaceStatus.MANTENIMIENTO,
            hourly_rate=Decimal("140"),
            capacity=10,
        )
    )

    assert output.id == existing.id
    assert output.name == "Sala Norte Renovada"
    assert output.status == SpaceStatus.MANTENIMIENTO
    assert output.hourly_rate == Decimal("140")
    assert output.capacity == 10
    assert uow.committed is True


def test_update_space_not_found() -> None:
    uow = FakeUnitOfWork(space_repository=FakeSpaceRepository())
    use_case = UpdateSpaceUseCase(uow)

    with pytest.raises(EntityNotFoundError):
        use_case.execute(
            UpdateSpaceInputDTO(
                space_id=uuid4(),
                name="Sala Inexistente",
                status=SpaceStatus.ACTIVO,
                hourly_rate=Decimal("100"),
                capacity=6,
            )
        )


def test_delete_space_happy_path() -> None:
    existing = _space()
    repository = FakeSpaceRepository([existing])
    uow = FakeUnitOfWork(space_repository=repository)
    use_case = DeleteSpaceUseCase(uow)

    use_case.execute(existing.id)

    assert repository.get_by_id(existing.id) is None
    assert uow.committed is True


def test_delete_space_not_found() -> None:
    uow = FakeUnitOfWork(space_repository=FakeSpaceRepository())
    use_case = DeleteSpaceUseCase(uow)

    with pytest.raises(EntityNotFoundError):
        use_case.execute(uuid4())
