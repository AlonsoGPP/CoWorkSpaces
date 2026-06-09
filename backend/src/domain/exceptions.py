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


class AuthenticationError(Exception):
    """Error de autenticacion para credenciales o token invalido."""


class InvalidCredentialsError(AuthenticationError):
    """Las credenciales del usuario no son validas."""


class AuthorizationError(Exception):
    """El usuario autenticado no tiene permisos o esta inactivo."""
