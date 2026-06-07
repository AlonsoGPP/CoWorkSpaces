from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.space import Space
from domain.exceptions import EntityNotFoundError, SpaceDeletionConflictError
from infrastructure.db.models import SpaceModel


class SqlAlchemySpaceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, space_id: UUID) -> Space | None:
        model = self._session.get(SpaceModel, space_id)
        if model is None:
            return None
        return self._to_domain(model)

    def list_all(self) -> list[Space]:
        rows = self._session.scalars(select(SpaceModel).order_by(SpaceModel.name)).all()
        return [self._to_domain(row) for row in rows]

    def add(self, space: Space) -> Space:
        model = SpaceModel(
            id=space.id,
            name=space.name,
            status=space.status,
            hourly_rate=space.hourly_rate,
            capacity=space.capacity,
        )
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def update(self, space: Space) -> Space:
        model = self._session.get(SpaceModel, space.id)
        if model is None:
            raise EntityNotFoundError("Espacio no encontrado")

        model.name = space.name
        model.status = space.status
        model.hourly_rate = space.hourly_rate
        model.capacity = space.capacity
        self._session.flush()
        return self._to_domain(model)

    def delete(self, space_id: UUID) -> None:
        model = self._session.get(SpaceModel, space_id)
        if model is None:
            raise EntityNotFoundError("Espacio no encontrado")

        self._session.delete(model)
        try:
            self._session.flush()
        except IntegrityError as error:
            sqlstate = getattr(getattr(error, "orig", None), "sqlstate", None)
            if sqlstate == "23503":
                raise SpaceDeletionConflictError(
                    "No se puede eliminar el espacio porque tiene reservas asociadas"
                ) from error
            raise error

    @staticmethod
    def _to_domain(model: SpaceModel) -> Space:
        return Space(
            id=model.id,
            name=model.name,
            status=model.status,
            hourly_rate=model.hourly_rate,
            capacity=model.capacity,
        )
