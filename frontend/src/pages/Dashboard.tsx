import { useAuth } from "../context/AuthContext";
import { useNotifications } from "../hooks/useNotifications";

export function Dashboard() {
  const { email, role } = useAuth();
  const notifications = useNotifications();

  return (
    <div className="page">
      <h1>Bienvenido/a, {email}</h1>
      <p>
        Tu rol es <strong>{role}</strong>. Usa el menu superior para gestionar cursos, estudiantes,
        matriculas y notas.
      </p>

      <section className="card">
        <h2>🔔 Notificaciones en tiempo real</h2>
        <p className="muted">
          Cuando un profesor registre una nota nueva para ti, aparecera aqui al instante (via
          WebSocket), sin recargar la pagina.
        </p>
        {notifications.length === 0 ? (
          <p className="muted">Sin notificaciones todavia.</p>
        ) : (
          <ul>
            {notifications.map((n) => (
              <li key={n.receivedAt}>
                <strong>{n.event}</strong>: {JSON.stringify(n.data)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
