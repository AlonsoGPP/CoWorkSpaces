from enum import Enum


class SpaceStatus(str, Enum):
    ACTIVO = "ACTIVO"
    MANTENIMIENTO = "MANTENIMIENTO"


class ReservationStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"
