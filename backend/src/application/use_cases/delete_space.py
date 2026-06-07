from uuid import UUID

from application.interfaces.unit_of_work import UnitOfWork


class DeleteSpaceUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, space_id: UUID) -> None:
        with self._unit_of_work as uow:
            uow.space_repository.delete(space_id)
            uow.commit()
