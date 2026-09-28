import { useEffect, useState, type FormEvent } from "react";
import { api, DAY_LABELS, type Course, type DayOfWeek, type Page, type Schedule } from "../api/client";
import { useAuth } from "../context/AuthContext";

const DAYS = Object.keys(DAY_LABELS) as DayOfWeek[];

const emptyForm = {
  course_id: "" as number | "",
  day_of_week: "monday" as DayOfWeek,
  start_time: "09:00",
  end_time: "11:00",
  classroom: "",
};

export function Schedules() {
  const { role } = useAuth();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  const canManage = role === "admin";

  const load = async () => {
    const { data } = await api.get<Page<Schedule>>("/schedules", { params: { limit: 100 } });
    // Orden de lectura natural: por dia de la semana y hora de inicio.
    const sorted = [...data.items].sort(
      (a, b) =>
        DAYS.indexOf(a.day_of_week) - DAYS.indexOf(b.day_of_week) || a.start_time.localeCompare(b.start_time)
    );
    setSchedules(sorted);
  };

  useEffect(() => {
    api.get<Page<Course>>("/courses", { params: { limit: 100 } }).then((res) => setCourses(res.data.items));
    load();
  }, []);

  const courseName = (id: number) => courses.find((c) => c.id === id)?.name ?? `#${id}`;

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    if (form.course_id === "") return;
    setError(null);
    if (form.end_time <= form.start_time) {
      setError("La hora de fin debe ser posterior a la de inicio.");
      return;
    }
    try {
      await api.post("/schedules", { ...form, classroom: form.classroom || null });
      setForm(emptyForm);
      await load();
    } catch {
      setError("No se pudo crear el horario.");
    }
  };

  const handleDelete = async (s: Schedule) => {
    if (!window.confirm(`¿Borrar el horario de ${courseName(s.course_id)} del ${DAY_LABELS[s.day_of_week]}?`)) return;
    await api.delete(`/schedules/${s.id}`);
    await load();
  };

  return (
    <div className="page">
      <h1>Horarios</h1>

      {canManage && (
        <form className="stacked-form" onSubmit={handleCreate}>
          <select
            aria-label="Curso"
            required
            value={form.course_id}
            onChange={(e) => setForm({ ...form, course_id: e.target.value === "" ? "" : Number(e.target.value) })}
          >
            <option value="">Selecciona un curso...</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <select
            aria-label="Dia"
            value={form.day_of_week}
            onChange={(e) => setForm({ ...form, day_of_week: e.target.value as DayOfWeek })}
          >
            {DAYS.map((d) => (
              <option key={d} value={d}>
                {DAY_LABELS[d]}
              </option>
            ))}
          </select>
          <input
            type="time"
            aria-label="Hora de inicio"
            required
            value={form.start_time}
            onChange={(e) => setForm({ ...form, start_time: e.target.value })}
          />
          <input
            type="time"
            aria-label="Hora de fin"
            required
            value={form.end_time}
            onChange={(e) => setForm({ ...form, end_time: e.target.value })}
          />
          <input
            placeholder="Aula"
            value={form.classroom}
            onChange={(e) => setForm({ ...form, classroom: e.target.value })}
          />
          <button type="submit">Crear horario</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dia</th>
              <th>Horario</th>
              <th>Curso</th>
              <th>Aula</th>
              {canManage && <th />}
            </tr>
          </thead>
          <tbody>
            {schedules.map((s) => (
              <tr key={s.id}>
                <td>{DAY_LABELS[s.day_of_week]}</td>
                <td>
                  {s.start_time.slice(0, 5)} - {s.end_time.slice(0, 5)}
                </td>
                <td>{courseName(s.course_id)}</td>
                <td>{s.classroom ?? "-"}</td>
                {canManage && (
                  <td>
                    <button className="danger" onClick={() => handleDelete(s)}>
                      Borrar
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
