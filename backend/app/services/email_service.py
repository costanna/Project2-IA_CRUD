"""Envio de emails transaccionales a traves de Resend (servicio externo).

Nivel Experto: "Integracion con servicios externos (pagos, notificaciones,
etc.)". Cuando se registra una nota, ademas del push por WebSocket (solo
llega si el estudiante esta conectado), se le envia un email.

Si `RESEND_API_KEY` no esta definida el envio se desactiva y solo se deja
constancia en el log, para que los tests y el desarrollo local no dependan
de la red ni de credenciales reales.
"""

from html import escape

import httpx

from app.core.config import settings
from app.core.logging_config import logger

RESEND_URL = "https://api.resend.com/emails"


class EmailService:
    def __init__(
        self,
        api_key: str | None = None,
        sender: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.resend_api_key
        self.sender = sender or settings.email_from
        # Permite inyectar un transporte falso en los tests (sin red).
        self.transport = transport

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def send(self, to: str, subject: str, html: str) -> bool:
        """Envia un email. Devuelve True si el proveedor lo acepto.

        Nunca lanza excepciones: un fallo del proveedor no debe romper la
        operacion principal (registrar la nota ya se ha completado).
        """
        if not self.enabled:
            logger.info("Email desactivado (sin RESEND_API_KEY): '%s' para %s", subject, to)
            return False
        try:
            async with httpx.AsyncClient(timeout=10, transport=self.transport) as client:
                response = await client.post(
                    RESEND_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"from": self.sender, "to": [to], "subject": subject, "html": html},
                )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("No se pudo enviar el email a %s: %s", to, exc)
            return False
        logger.info("Email enviado a %s: '%s'", to, subject)
        return True

    async def send_new_grade(
        self, to: str, student_name: str, course: str, evaluation: str, score: float
    ) -> bool:
        subject = f"Nueva nota en {course}"
        html = (
            f"<p>Hola {escape(student_name)},</p>"
            f"<p>Tienes una nota nueva en <strong>{escape(course)}</strong>:</p>"
            f"<p>{escape(evaluation)}: <strong>{score:g}</strong> / 10</p>"
            "<p>Academia F5</p>"
        )
        return await self.send(to, subject, html)
