from application.dto.space_dto import SpaceOutputDTO, UpdateSpaceInputDTO
from application.interfaces.unit_of_work import UnitOfWork
from domain.entities.space import Space
from domain.exceptions import EntityNotFoundError


class UpdateSpaceUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, input_dto: UpdateSpaceInputDTO) -> SpaceOutputDTO:
        with self._unit_of_work as uow:
            current_space = uow.space_repository.get_by_id(input_dto.space_id)
            if current_space is None:
                raise EntityNotFoundError("Espacio no encontrado")

            space = Space(
                id=current_space.id,
                name=input_dto.name,
                status=input_dto.status,
                hourly_rate=input_dto.hourly_rate,
                capacity=input_dto.capacity,
            )

            updated = uow.space_repository.update(space)
            uow.commit()

        return SpaceOutputDTO(
            id=updated.id,
            name=updated.name,
            status=updated.status,
            hourly_rate=updated.hourly_rate,
            capacity=updated.capacity,
        )
