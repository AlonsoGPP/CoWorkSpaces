from application.dto.space_dto import SpaceOutputDTO
from application.interfaces.unit_of_work import UnitOfWork


class ListSpacesUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self) -> list[SpaceOutputDTO]:
        with self._unit_of_work as uow:
            spaces = uow.space_repository.list_all()

        return [
            SpaceOutputDTO(
                id=space.id,
                name=space.name,
                status=space.status,
                hourly_rate=space.hourly_rate,
                capacity=space.capacity,
            )
            for space in spaces
        ]
