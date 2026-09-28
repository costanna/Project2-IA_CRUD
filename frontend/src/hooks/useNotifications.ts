import { useEffect, useRef, useState } from "react";
import { useAuth } from "../context/AuthContext";

export interface Notification {
  event: string;
  data: Record<string, unknown>;
  receivedAt: number;
}

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000/ws/notifications";
const RECONNECT_DELAY_MS = 3000;

/**
 * Se conecta al canal de websocket de notificaciones y acumula los eventos
 * recibidos (p.ej. "new_grade" cuando un profesor publica una nota). Si la
 * conexion se corta (reinicio del servidor, proxy que cierra conexiones
 * inactivas...), se reconecta sola. `onEvent` permite reaccionar a cada
 * evento, por ejemplo recargando datos.
 */
export function useNotifications(onEvent?: (notification: Notification) => void): Notification[] {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!token) return;

    let socket: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | undefined;
    let closedByUs = false;

    const connect = () => {
      socket = new WebSocket(`${WS_URL}?token=${token}`);

      socket.onmessage = (event) => {
        const notification = { ...JSON.parse(event.data), receivedAt: Date.now() } as Notification;
        setNotifications((prev) => [notification, ...prev].slice(0, 20));
        onEventRef.current?.(notification);
      };

      socket.onclose = (event) => {
        // 4401 = token invalido: reintentar no serviria de nada.
        if (!closedByUs && event.code !== 4401) {
          retry = setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };
    };

    connect();

    return () => {
      closedByUs = true;
      clearTimeout(retry);
      socket?.close();
    };
  }, [token]);

  return notifications;
}
