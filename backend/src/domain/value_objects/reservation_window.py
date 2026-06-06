from dataclasses import dataclass
from datetime import datetime, timedelta

from domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ReservationWindow:
    start_at: datetime
    end_at: datetime

    MIN_DURATION: timedelta = timedelta(minutes=30)
    MAX_DURATION: timedelta = timedelta(hours=8)

    def __post_init__(self) -> None:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValidationError("Las fechas de reserva deben incluir zona horaria")
        if self.end_at <= self.start_at:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio")
        if self.duration < self.MIN_DURATION:
            raise ValidationError("La duracion minima de reserva es 30 minutos")
        if self.duration > self.MAX_DURATION:
            raise ValidationError("La duracion maxima de reserva es 8 horas")

    @property
    def duration(self) -> timedelta:
        return self.end_at - self.start_at

    @property
    def duration_hours(self) -> float:
        return self.duration.total_seconds() / 3600
