import { useEffect, useState, type FormEvent } from "react";
import { api, type Enrollment, type Grade, type Page } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface EditState {
  id: number;
  evaluation_name: string;
  score: number;
}

export function Grades() {
  const { role } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [selectedEnrollment, setSelectedEnrollment] = useState<number | "">("");
  const [grades, setGrades] = useState<Grade[]>([]);
  const [evaluationName, setEvaluationName] = useState("");
  const [score, setScore] = useState(5);
  const [editing, setEditing] = useState<EditState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canGrade = role === "admin" || role === "teacher";

  useEffect(() => {
    // Para estudiantes la API ya devuelve solo sus matriculas.
    api
      .get<Page<Enrollment>>("/enrollments", { params: { limit: 100 } })
      .then((res) => setEnrollments(res.data.items));
  }, []);

  const loadGrades = async (enrollmentId: number) => {
    const { data } = await api.get<Page<Grade>>("/grades", {
      params: { enrollment_id: enrollmentId, limit: 100 },
    });
    setGrades(data.items);
  };

  useEffect(() => {
    setEditing(null);
    if (selectedEnrollment !== "") {
      loadGrades(selectedEnrollment);
    } else {
      setGrades([]);
    }
  }, [selectedEnrollment]);

  const handleAddGrade = async (event: FormEvent) => {
    event.preventDefault();
    if (selectedEnrollment === "") return;
    setError(null);
    try {
      await api.post("/grades", {
        enrollment_id: selectedEnrollment,
        evaluation_name: evaluationName,
        score,
      });
      setEvaluationName("");
      setScore(5);
      await loadGrades(selectedEnrollment);
    } catch {
      setError("No se pudo registrar la nota.");
    }
  };

  const handleSave = async () => {
    if (!editing || selectedEnrollment === "") return;
    setError(null);
    try {
      await api.put(`/grades/${editing.id}`, {
        evaluation_name: editing.evaluation_name,
        score: editing.score,
      });
      setEditing(null);
      await loadGrades(selectedEnrollment);
    } catch {
      setError("No se pudo guardar la nota (debe estar entre 0 y 10).");
    }
  };

  const handleDelete = async (g: Grade) => {
    if (selectedEnrollment === "" || !window.confirm(`¿Borrar la nota "${g.evaluation_name}"?`)) return;
    await api.delete(`/grades/${g.id}`);
    await loadGrades(selectedEnrollment);
  };

  const average = grades.length ? grades.reduce((sum, g) => sum + g.score, 0) / grades.length : null;

  return (
    <div className="page">
      <h1>Notas</h1>

      <label htmlFor="enrollment">Matricula</label>
      <select
        id="enrollment"
        value={selectedEnrollment}
        onChange={(e) => setSelectedEnrollment(e.target.value === "" ? "" : Number(e.target.value))}
      >
        <option value="">Selecciona una matricula...</option>
        {enrollments.map((en) => (
          <option key={en.id} value={en.id}>
            {en.student_name} · {en.course_name}
          </option>
        ))}
      </select>

      {canGrade && selectedEnrollment !== "" && (
        <form className="inline-form" onSubmit={handleAddGrade}>
          <input
            placeholder="Evaluacion (ej. Parcial 1)"
            required
            value={evaluationName}
            onChange={(e) => setEvaluationName(e.target.value)}
          />
          <input
            type="number"
            aria-label="Nota"
            min={0}
            max={10}
            step={0.1}
            value={score}
            onChange={(e) => setScore(Number(e.target.value))}
          />
          <button type="submit">Registrar nota</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      {average !== null && (
        <p className="muted">
          Media: <strong>{average.toFixed(2)}</strong> ({grades.length} notas)
        </p>
      )}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Evaluacion</th>
              <th>Nota</th>
              <th>Fecha</th>
              {canGrade && <th />}
            </tr>
          </thead>
          <tbody>
            {grades.map((g) =>
              editing?.id === g.id ? (
                <tr key={g.id}>
                  <td>
                    <input
                      aria-label="Evaluacion"
                      value={editing.evaluation_name}
                      onChange={(e) => setEditing({ ...editing, evaluation_name: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      aria-label="Nota"
                      min={0}
                      max={10}
                      step={0.1}
                      value={editing.score}
                      onChange={(e) => setEditing({ ...editing, score: Number(e.target.value) })}
                    />
                  </td>
                  <td>{new Date(g.date).toLocaleDateString()}</td>
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
                <tr key={g.id}>
                  <td>{g.evaluation_name}</td>
                  <td>{g.score}</td>
                  <td>{new Date(g.date).toLocaleDateString()}</td>
                  {canGrade && (
                    <td>
                      <div className="row-actions">
                        <button
                          className="secondary"
                          onClick={() =>
                            setEditing({ id: g.id, evaluation_name: g.evaluation_name, score: g.score })
                          }
                        >
                          Editar
                        </button>
                        <button className="danger" onClick={() => handleDelete(g)}>
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
    </div>
  );
}
