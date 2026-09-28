import { useCallback, useEffect, useState } from "react";
import { api, type Enrollment, type Grade, type Page } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useNotifications } from "../hooks/useNotifications";

const RECENT_GRADES = 5;

interface RecentGrade extends Grade {
  course_name: string;
}

export function Dashboard() {
  const { email, role } = useAuth();
  const isStudent = role === "student";
  const [recentGrades, setRecentGrades] = useState<RecentGrade[]>([]);

  // Las notas quedan guardadas en la API: el estudiante las ve aunque no
  // estuviera conectado cuando se publicaron. El WebSocket solo avisa al
  // instante de las nuevas mientras el dashboard esta abierto.
  const loadRecentGrades = useCallback(async () => {
    const [enrollments, grades] = await Promise.all([
      api.get<Page<Enrollment>>("/enrollments", { params: { limit: 100 } }),
      api.get<Page<Grade>>("/grades", { params: { limit: 100 } }),
    ]);
    const courseByEnrollment = new Map(enrollments.data.items.map((e) => [e.id, e.course_name]));
    const latest = [...grades.data.items]
      .sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id)
      .slice(0, RECENT_GRADES)
      .map((g) => ({ ...g, course_name: courseByEnrollment.get(g.enrollment_id) ?? "-" }));
    setRecentGrades(latest);
  }, []);

  const notifications = useNotifications((notification) => {
    if (notification.event === "new_grade") loadRecentGrades();
  });

  useEffect(() => {
    if (isStudent) loadRecentGrades();
  }, [isStudent, loadRecentGrades]);

  const newGrades = notifications.filter((n) => n.event === "new_grade");

  return (
    <div className="page">
      <h1>Bienvenido/a, {email}</h1>
      <p>
        Tu rol es <strong>{role}</strong>. Usa el menu superior para gestionar cursos, estudiantes,
        matriculas y notas.
      </p>

      {isStudent && (
        <section className="card">
          <h2>🔔 Notificaciones en tiempo real</h2>
          {newGrades.length === 0 ? (
            <p className="muted">
              Cuando un profesor te ponga una nota con esta pagina abierta, aparecera aqui al instante.
            </p>
          ) : (
            <ul className="notifications">
              {newGrades.map((n) => (
                <li key={n.receivedAt}>
                  <span className="badge">Nueva</span> Nota de <strong>{String(n.data.score)}</strong> en{" "}
                  {String(n.data.evaluation_name)} ({String(n.data.course)}) —{" "}
                  {new Date(n.receivedAt).toLocaleTimeString()}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {isStudent && (
        <section className="card">
          <h2>📝 Tus ultimas notas</h2>
          {recentGrades.length === 0 ? (
            <p className="muted">Todavia no tienes notas.</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Curso</th>
                    <th>Evaluacion</th>
                    <th>Nota</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {recentGrades.map((g) => (
                    <tr key={g.id}>
                      <td>{g.course_name}</td>
                      <td>{g.evaluation_name}</td>
                      <td>{g.score}</td>
                      <td>{new Date(g.date).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
