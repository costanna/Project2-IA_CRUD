import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";

export interface Notification {
  event: string;
  data: Record<string, unknown>;
  receivedAt: number;
}

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/notifications";

/**
 * Se conecta al canal de websocket de notificaciones y acumula los eventos
 * recibidos (p.ej. "new_grade" cuando un profesor publica una nota). Sirve
 * de base para la experiencia "dinamica" del dashboard: sin este hook el
 * estudiante tendria que refrescar la pagina para enterarse de una nota
 * nueva.
 */
export function useNotifications(): Notification[] {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    if (!token) return;

    const socket = new WebSocket(`${WS_URL}?token=${token}`);

    socket.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setNotifications((prev) => [{ ...parsed, receivedAt: Date.now() }, ...prev].slice(0, 20));
    };

    return () => socket.close();
  }, [token]);

  return notifications;
}
