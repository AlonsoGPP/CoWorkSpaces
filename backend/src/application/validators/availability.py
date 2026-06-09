from domain.exceptions import ValidationError


def validate_slot_minutes(slot_minutes: int) -> None:
    if slot_minutes < 15:
        raise ValidationError("El tamano minimo del slot es 15 minutos")
    if slot_minutes > 120:
        raise ValidationError("El tamano maximo del slot es 120 minutos")
    if slot_minutes % 5 != 0:
        raise ValidationError(
            "El tamano del slot debe estar en incrementos de 5 minutos"
        )
