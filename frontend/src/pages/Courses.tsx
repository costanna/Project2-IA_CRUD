import { useEffect, useState, type FormEvent } from "react";
import { api, downloadCsv, type Course, type Page, type Teacher } from "../api/client";
import { useAuth } from "../context/AuthContext";

const PAGE_SIZE = 5;

interface CourseForm {
  name: string;
  description: string;
  credits: number;
  teacher_id: number | "";
}

const emptyForm: CourseForm = { name: "", description: "", credits: 1, teacher_id: "" };

const toPayload = (form: CourseForm) => ({
  name: form.name,
  description: form.description || null,
  credits: form.credits,
  teacher_id: form.teacher_id === "" ? null : form.teacher_id,
});

export function Courses() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Course> | null>(null);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [skip, setSkip] = useState(0);
  const [form, setForm] = useState<CourseForm>(emptyForm);
  const [editing, setEditing] = useState<(CourseForm & { id: number }) | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canManage = role === "admin";

  const loadCourses = async (newSkip: number) => {
    const { data } = await api.get<Page<Course>>("/courses", {
      params: { skip: newSkip, limit: PAGE_SIZE },
    });
    setPage(data);
    setSkip(newSkip);
  };

  useEffect(() => {
    loadCourses(0);
    api
      .get<Page<Teacher>>("/teachers", { params: { limit: 100 } })
      .then((res) => setTeachers(res.data.items));
  }, []);

  const teacherName = (id: number | null) => {
    if (id === null) return "Sin asignar";
    const t = teachers.find((teacher) => teacher.id === id);
    return t ? `${t.first_name} ${t.last_name}` : `#${id}`;
  };

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("/courses", toPayload(form));
      setForm(emptyForm);
      await loadCourses(0);
    } catch {
      setError("No se pudo crear el curso.");
    }
  };

  const handleSave = async () => {
    if (!editing) return;
    setError(null);
    try {
      await api.put(`/courses/${editing.id}`, toPayload(editing));
      setEditing(null);
      await loadCourses(skip);
    } catch {
      setError("No se pudieron guardar los cambios.");
    }
  };

  const handleDelete = async (course: Course) => {
    if (!window.confirm(`¿Borrar el curso "${course.name}"? Se borraran sus matriculas y notas.`)) return;
    await api.delete(`/courses/${course.id}`);
    await loadCourses(0);
  };

  const teacherSelect = (value: number | "", onChange: (value: number | "") => void) => (
    <select
      aria-label="Profesor"
      value={value}
      onChange={(e) => onChange(e.target.value === "" ? "" : Number(e.target.value))}
    >
      <option value="">Sin profesor</option>
      {teachers.map((t) => (
        <option key={t.id} value={t.id}>
          {t.first_name} {t.last_name}
        </option>
      ))}
    </select>
  );

  return (
    <div className="page">
      <div className="toolbar">
        <h1>Cursos</h1>
        {canManage && (
          <button className="secondary" onClick={() => downloadCsv("/courses/export", "courses.csv")}>
            Exportar CSV
          </button>
        )}
      </div>

      {canManage && (
        <form className="stacked-form" onSubmit={handleCreate}>
          <input
            placeholder="Nombre del curso"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
          <input
            placeholder="Descripcion"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <input
            type="number"
            aria-label="Creditos"
            min={1}
            max={12}
            value={form.credits}
            onChange={(e) => setForm({ ...form, credits: Number(e.target.value) })}
          />
          {teacherSelect(form.teacher_id, (teacher_id) => setForm({ ...form, teacher_id }))}
          <button type="submit">Crear curso</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Descripcion</th>
              <th>Creditos</th>
              <th>Profesor</th>
              {canManage && <th />}
            </tr>
          </thead>
          <tbody>
            {page?.items.map((course) =>
              editing?.id === course.id ? (
                <tr key={course.id}>
                  <td>{course.id}</td>
                  <td>
                    <input
                      aria-label="Nombre"
                      value={editing.name}
                      onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      aria-label="Descripcion"
                      value={editing.description}
                      onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label="Creditos"
                      min={1}
                      max={12}
                      value={editing.credits}
                      onChange={(e) => setEditing({ ...editing, credits: Number(e.target.value) })}
                    />
                  </td>
                  <td>{teacherSelect(editing.teacher_id, (teacher_id) => setEditing({ ...editing, teacher_id }))}</td>
                  <td>
                    <div className="row-actions">
                      <button onClick={handleSave}>Guardar</button>
                      <button className="secondary" onClick={() => setEditing(null)}>
                        Cancelar
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={course.id}>
                  <td>{course.id}</td>
                  <td>{course.name}</td>
                  <td>{course.description ?? "-"}</td>
                  <td>{course.credits}</td>
                  <td>{teacherName(course.teacher_id)}</td>
                  {canManage && (
                    <td>
                      <div className="row-actions">
                        <button
                          className="secondary"
                          onClick={() =>
                            setEditing({
                              id: course.id,
                              name: course.name,
                              description: course.description ?? "",
                              credits: course.credits,
                              teacher_id: course.teacher_id ?? "",
                            })
                          }
                        >
                          Editar
                        </button>
                        <button className="danger" onClick={() => handleDelete(course)}>
                          Borrar
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>

      {page && (
        <div className="pagination">
          <button disabled={skip === 0} onClick={() => loadCourses(Math.max(0, skip - PAGE_SIZE))}>
            Anterior
          </button>
          <span>
            {page.total === 0 ? 0 : skip + 1}-{Math.min(skip + PAGE_SIZE, page.total)} de {page.total}
          </span>
          <button
            disabled={skip + PAGE_SIZE >= page.total}
            onClick={() => loadCourses(skip + PAGE_SIZE)}
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}
