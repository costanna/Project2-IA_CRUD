import { useEffect, useState, type FormEvent } from "react";
import { api, type Enrollment, type Grade, type Page } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function Grades() {
  const { role } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [selectedEnrollment, setSelectedEnrollment] = useState<number | "">("");
  const [grades, setGrades] = useState<Grade[]>([]);
  const [evaluationName, setEvaluationName] = useState("");
  const [score, setScore] = useState(5);
  const [error, setError] = useState<string | null>(null);

  const canGrade = role === "admin" || role === "teacher";

  useEffect(() => {
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
            Matricula #{en.id} (estudiante {en.student_id}, curso {en.course_id})
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

      <table>
        <thead>
          <tr>
            <th>Evaluacion</th>
            <th>Nota</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {grades.map((g) => (
            <tr key={g.id}>
              <td>{g.evaluation_name}</td>
              <td>{g.score}</td>
              <td>{new Date(g.date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
