import { useEffect, useState, type FormEvent } from "react";
import { api, type Course, type Page } from "../api/client";
import { useAuth } from "../context/AuthContext";

const PAGE_SIZE = 5;

export function Courses() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Course> | null>(null);
  const [skip, setSkip] = useState(0);
  const [name, setName] = useState("");
  const [credits, setCredits] = useState(1);
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
  }, []);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("/courses", { name, credits });
      setName("");
      setCredits(1);
      await loadCourses(0);
    } catch {
      setError("No se pudo crear el curso.");
    }
  };

  const handleExport = async () => {
    const response = await api.get("/courses/export", { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = "courses.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page">
      <h1>Cursos</h1>

      {canManage && (
        <form className="inline-form" onSubmit={handleCreate}>
          <input
            placeholder="Nombre del curso"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="number"
            min={1}
            max={12}
            value={credits}
            onChange={(e) => setCredits(Number(e.target.value))}
          />
          <button type="submit">Crear curso</button>
          <button type="button" onClick={handleExport}>
            Exportar CSV
          </button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Creditos</th>
            <th>Profesor</th>
          </tr>
        </thead>
        <tbody>
          {page?.items.map((course) => (
            <tr key={course.id}>
              <td>{course.id}</td>
              <td>{course.name}</td>
              <td>{course.credits}</td>
              <td>{course.teacher_id ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {page && (
        <div className="pagination">
          <button disabled={skip === 0} onClick={() => loadCourses(Math.max(0, skip - PAGE_SIZE))}>
            Anterior
          </button>
          <span>
            {skip + 1}-{Math.min(skip + PAGE_SIZE, page.total)} de {page.total}
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
