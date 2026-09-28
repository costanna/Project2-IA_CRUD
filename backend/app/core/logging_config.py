"""Configuracion basica de logging para toda la app.

Nivel Esencial pide "Logging basico". Configuramos un logger raiz que
escribe en consola con timestamp, nivel, logger y mensaje, y un logger de
acceso para request/response.
"""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # Silenciamos ruido de librerias de terceros en nivel INFO
    logging.getLogger("passlib").setLevel(logging.ERROR)


logger = logging.getLogger("academia")
