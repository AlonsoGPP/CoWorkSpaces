from presentation.schemas.common import ErrorResponse

DEFAULT_ERROR_RESPONSES = {
    400: {
        "description": "Error de negocio o solicitud invalida",
        "model": ErrorResponse,
    },
    404: {
        "description": "Recurso no encontrado",
        "model": ErrorResponse,
    },
    409: {
        "description": "Conflicto de estado o concurrencia",
        "model": ErrorResponse,
    },
    422: {
        "description": "Error de validacion",
        "model": ErrorResponse,
    },
    500: {
        "description": "Error interno del servidor",
        "model": ErrorResponse,
    },
}
