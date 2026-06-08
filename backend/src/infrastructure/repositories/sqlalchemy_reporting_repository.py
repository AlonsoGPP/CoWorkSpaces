from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from application.dto.report_dto import OccupancyBySpaceRowDTO
from domain.enums import ReservationStatus
from infrastructure.db.models import ReservationModel, SpaceModel


class SqlAlchemyReportingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_occupancy_by_space(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> list[OccupancyBySpaceRowDTO]:
        overlap_minutes = (
            func.extract(
                "epoch",
                func.least(ReservationModel.end_at, end_at)
                - func.greatest(ReservationModel.start_at, start_at),
            )
            / 60.0
        )

        query = (
            select(
                SpaceModel.id,
                SpaceModel.name,
                func.coalesce(func.sum(overlap_minutes), 0.0).label("occupied_minutes"),
                func.count(ReservationModel.id).label("reservations_count"),
            )
            .select_from(SpaceModel)
            .join(
                ReservationModel,
                and_(
                    ReservationModel.space_id == SpaceModel.id,
                    ReservationModel.end_at > start_at,
                    ReservationModel.start_at < end_at,
                    ReservationModel.status.in_(
                        [
                            ReservationStatus.PENDIENTE,
                            ReservationStatus.CONFIRMADA,
                            ReservationStatus.COMPLETADA,
                        ]
                    ),
                ),
                isouter=True,
            )
            .group_by(SpaceModel.id, SpaceModel.name)
            .order_by(SpaceModel.name)
        )

        rows = self._session.execute(query).all()
        return [
            OccupancyBySpaceRowDTO(
                space_id=row.id,
                space_name=row.name,
                occupied_minutes=Decimal(str(row.occupied_minutes)),
                reservations_count=int(row.reservations_count),
            )
            for row in rows
        ]

    def get_revenue_by_range(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> Decimal:
        query = select(
            func.coalesce(func.sum(ReservationModel.total_price), Decimal("0"))
        ).where(
            ReservationModel.start_at >= start_at,
            ReservationModel.start_at < end_at,
            ReservationModel.status.in_(
                [ReservationStatus.CONFIRMADA, ReservationStatus.COMPLETADA]
            ),
        )
        total_revenue = self._session.scalar(query)
        return Decimal(str(total_revenue or Decimal("0")))

    def get_reservations_count_by_status(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
    ) -> dict[ReservationStatus, int]:
        query = (
            select(ReservationModel.status, func.count(ReservationModel.id))
            .where(
                ReservationModel.start_at >= start_at,
                ReservationModel.start_at < end_at,
            )
            .group_by(ReservationModel.status)
        )

        rows = self._session.execute(query).all()
        return {status: int(count) for status, count in rows}
