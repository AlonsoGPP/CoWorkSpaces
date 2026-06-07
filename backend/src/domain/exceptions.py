class DomainError(Exception):
    """Base para errores de dominio."""


class ValidationError(DomainError):
    """Error de validacion de reglas de negocio."""


class EntityNotFoundError(DomainError):
    """Entidad no encontrada en el dominio."""


class SpaceUnavailableError(DomainError):
    """El espacio no puede aceptar reservas."""


class SpaceDeletionConflictError(DomainError):
    """No se puede eliminar un espacio por dependencias existentes."""


class OverlappingReservationError(DomainError):
    """Conflicto de reserva por solapamiento de horario."""


class ReservationNotCancelableError(DomainError):
    """La reserva no puede cancelarse por su estado o ventana temporal."""
