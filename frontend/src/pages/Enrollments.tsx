import { useEffect, useState } from "react";
import { api, type Course, type Enrollment, type Page, type Student } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function Enrollments() {
  const { role } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [myStudentId, setMyStudentId] = useState<number | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    const coursesResponse = await api.get<Page<Course>>("/courses", { params: { limit: 100 } });
    setCourses(coursesResponse.data.items);

    if (role === "student") {
      const me = await api.get<Student>("/students/me");
      setMyStudentId(me.data.id);
      const mine = await api.get<Page<Enrollment>>("/enrollments", {
        params: { student_id: me.data.id, limit: 100 },
      });
      setEnrollments(mine.data.items);
    } else {
      const all = await api.get<Page<Enrollment>>("/enrollments", { params: { limit: 100 } });
      setEnrollments(all.data.items);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const courseName = (id: number) => courses.find((c) => c.id === id)?.name ?? id;

  const handleEnroll = async () => {
    if (!myStudentId || selectedCourse === "") return;
    setError(null);
    try {
      await api.post("/enrollments", { student_id: myStudentId, course_id: selectedCourse });
      await load();
    } catch {
      setError("No se pudo completar la matricula (¿ya estas matriculado en ese curso?).");
    }
  };

  return (
    <div className="page">
      <h1>Matriculas</h1>

      {role === "student" && (
        <div className="inline-form">
          <select value={selectedCourse} onChange={(e) => setSelectedCourse(Number(e.target.value))}>
            <option value="">Selecciona un curso...</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <button onClick={handleEnroll} disabled={selectedCourse === ""}>
            Matricularme
          </button>
        </div>
      )}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Estudiante</th>
            <th>Curso</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {enrollments.map((e) => (
            <tr key={e.id}>
              <td>{e.id}</td>
              <td>{e.student_id}</td>
              <td>{courseName(e.course_id)}</td>
              <td>{e.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
