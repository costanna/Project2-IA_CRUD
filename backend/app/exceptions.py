"""Excepciones de dominio y sus handlers HTTP.

Nivel Esencial: "Manejo de excepciones simple".
Nivel Medio: "Manejo avanzado de errores con codigos HTTP apropiados".

Cada excepcion de dominio se traduce a un codigo HTTP concreto en un unico
sitio (main.py), en vez de repartir `HTTPException` con codigos ad-hoc por
todos los routers/servicios.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logging_config import logger


class AppError(Exception):
    """Excepcion base de la aplicacion."""

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


class ValidationError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError en %s: %s", request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor."},
    )
