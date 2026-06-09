from datetime import datetime

from domain.exceptions import ValidationError


def validate_report_range(*, start_at: datetime, end_at: datetime) -> None:
    if start_at.tzinfo is None or end_at.tzinfo is None:
        raise ValidationError("Las fechas del reporte deben incluir zona horaria")
    if end_at <= start_at:
        raise ValidationError(
            "La fecha de fin del reporte debe ser posterior a la fecha de inicio"
        )
