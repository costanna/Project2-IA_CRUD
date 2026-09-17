"""Gestor de conexiones WebSocket para notificaciones en tiempo real.

Nivel Avanzado: "Implementacion de websockets para actualizaciones en
tiempo real". Cuando un profesor/admin publica una nota, el estudiante
duenio de la matricula (si esta conectado) recibe un push inmediato en
lugar de tener que hacer polling a la API.
"""

import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # user_email -> conjunto de sockets activos (permite varias pestanas)
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, user_email: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_email, set()).add(websocket)

    def disconnect(self, user_email: str, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_email)
        if sockets:
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(user_email, None)

    async def notify_user(self, user_email: str, event: str, payload: dict) -> None:
        sockets = self._connections.get(user_email, set())
        message = json.dumps({"event": event, "data": payload})
        for socket in list(sockets):
            await socket.send_text(message)


manager = ConnectionManager()
