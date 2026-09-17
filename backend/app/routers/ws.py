from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.services.notification_service import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/notifications")
async def notifications_endpoint(websocket: WebSocket, token: str) -> None:
    """Canal de notificaciones en tiempo real.

    El cliente se conecta con `?token=<jwt>`; el token identifica al
    usuario y se reutiliza el mismo esquema de autenticacion que la API
    REST. Cuando se publica una nota nueva, `GradeService` empuja un evento
    `new_grade` al estudiante correspondiente por este canal.
    """
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        await websocket.close(code=4401)
        return

    user_email = payload["sub"]
    await manager.connect(user_email, websocket)
    try:
        while True:
            # Mantenemos la conexion viva; no esperamos mensajes del cliente.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_email, websocket)
