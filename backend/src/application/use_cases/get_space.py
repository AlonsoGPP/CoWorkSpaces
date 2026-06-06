from uuid import UUID

from application.dto.space_dto import SpaceOutputDTO
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import EntityNotFoundError


class GetSpaceUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, space_id: UUID) -> SpaceOutputDTO:
        with self._unit_of_work as uow:
            space = uow.space_repository.get_by_id(space_id)

        if space is None:
            raise EntityNotFoundError("Espacio no encontrado")

        return SpaceOutputDTO(
            id=space.id,
            name=space.name,
            status=space.status,
            hourly_rate=space.hourly_rate,
            capacity=space.capacity,
        )
