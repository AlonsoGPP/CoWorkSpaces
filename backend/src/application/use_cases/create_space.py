from uuid import uuid4

from application.dto.space_dto import CreateSpaceInputDTO, SpaceOutputDTO
from application.interfaces.unit_of_work import UnitOfWork
from domain.entities.space import Space


class CreateSpaceUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, input_dto: CreateSpaceInputDTO) -> SpaceOutputDTO:
        space = Space(
            id=uuid4(),
            name=input_dto.name,
            status=input_dto.status,
            hourly_rate=input_dto.hourly_rate,
            capacity=input_dto.capacity,
        )

        with self._unit_of_work as uow:
            created = uow.space_repository.add(space)
            uow.commit()

        return SpaceOutputDTO(
            id=created.id,
            name=created.name,
            status=created.status,
            hourly_rate=created.hourly_rate,
            capacity=created.capacity,
        )
