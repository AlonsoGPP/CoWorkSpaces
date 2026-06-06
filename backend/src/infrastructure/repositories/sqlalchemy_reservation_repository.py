from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.reservation import Reservation
from domain.exceptions import EntityNotFoundError, OverlappingReservationError
from domain.value_objects.reservation_window import ReservationWindow
from infrastructure.db.models import ReservationModel


class SqlAlchemyReservationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, reservation: Reservation) -> Reservation:
        model = ReservationModel(
            id=reservation.id,
            space_id=reservation.space_id,
            start_at=reservation.reservation_window.start_at,
            end_at=reservation.reservation_window.end_at,
            status=reservation.status,
            total_price=reservation.total_price,
            created_at=reservation.created_at,
            cancelled_at=reservation.cancelled_at,
        )
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError as error:
            self._map_integrity_error(error)
        return self._to_domain(model)

    def get_by_id(self, reservation_id: UUID) -> Reservation | None:
        model = self._session.get(ReservationModel, reservation_id)
        if model is None:
            return None
        return self._to_domain(model)

    def list_by_space(self, space_id: UUID) -> list[Reservation]:
        rows = self._session.scalars(
            select(ReservationModel)
            .where(ReservationModel.space_id == space_id)
            .order_by(ReservationModel.start_at)
        ).all()
        return [self._to_domain(row) for row in rows]

    def update(self, reservation: Reservation) -> Reservation:
        model = self._session.get(ReservationModel, reservation.id)
        if model is None:
            raise EntityNotFoundError("Reserva no encontrada")

        model.space_id = reservation.space_id
        model.start_at = reservation.reservation_window.start_at
        model.end_at = reservation.reservation_window.end_at
        model.status = reservation.status
        model.total_price = reservation.total_price
        model.cancelled_at = reservation.cancelled_at

        try:
            self._session.flush()
        except IntegrityError as error:
            self._map_integrity_error(error)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: ReservationModel) -> Reservation:
        return Reservation(
            id=model.id,
            space_id=model.space_id,
            reservation_window=ReservationWindow(
                start_at=model.start_at,
                end_at=model.end_at,
            ),
            status=model.status,
            total_price=model.total_price,
            created_at=model.created_at,
            cancelled_at=model.cancelled_at,
        )

    @staticmethod
    def _map_integrity_error(error: IntegrityError) -> None:
        error_detail = str(getattr(error, "orig", error))
        if "reservations_no_overlap" in error_detail:
            raise OverlappingReservationError(
                "Ya existe una reserva en ese rango para este espacio"
            ) from error
        raise error
