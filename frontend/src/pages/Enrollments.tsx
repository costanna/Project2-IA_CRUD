import { useEffect, useState } from "react";
import {
  api,
  ENROLLMENT_STATUS_LABELS,
  type Course,
  type Enrollment,
  type EnrollmentStatus,
  type Page,
  type Student,
  type Teacher,
} from "../api/client";
import { useAuth } from "../context/AuthContext";

export function Enrollments() {
  const { role } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [myStudentId, setMyStudentId] = useState<number | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<number | "">("");
  const [selectedCourse, setSelectedCourse] = useState<number | "">("");
  const [courseFilter, setCourseFilter] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  const isStudent = role === "student";
  const isStaff = role === "admin" || role === "teacher";

  const loadEnrollments = async (courseId: number | "" = courseFilter) => {
    // Para estudiantes la API ya limita el listado a sus propias matriculas.
    const { data } = await api.get<Page<Enrollment>>("/enrollments", {
      params: { limit: 100, course_id: courseId === "" ? undefined : courseId },
    });
    setEnrollments(data.items);
  };

  useEffect(() => {
    // Un profesor solo puede matricular en los cursos que imparte.
    const loadCourses = async () => {
      const teacherId =
        role === "teacher" ? (await api.get<Teacher>("/teachers/me")).data.id : undefined;
      const { data } = await api.get<Page<Course>>("/courses", {
        params: { limit: 100, teacher_id: teacherId },
      });
      setCourses(data.items);
    };
    loadCourses();
    if (isStudent) {
      api.get<Student>("/students/me").then((res) => setMyStudentId(res.data.id));
    } else if (isStaff) {
      api
        .get<Page<Student>>("/students", { params: { limit: 100 } })
        .then((res) => setStudents(res.data.items));
    }
    loadEnrollments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const studentId = isStudent ? myStudentId : selectedStudent === "" ? null : selectedStudent;

  const handleEnroll = async () => {
    if (studentId === null || selectedCourse === "") return;
    setError(null);
    try {
      await api.post("/enrollments", { student_id: studentId, course_id: selectedCourse });
      setSelectedCourse("");
      setSelectedStudent("");
      await loadEnrollments();
    } catch {
      setError("No se pudo completar la matricula (¿ese estudiante ya esta en el curso?).");
    }
  };

  const handleStatus = async (id: number, status: EnrollmentStatus) => {
    setError(null);
    try {
      await api.put(`/enrollments/${id}`, { status });
      await loadEnrollments();
    } catch {
      setError("No se pudo cambiar el estado.");
    }
  };

  const handleDelete = async (e: Enrollment) => {
    if (!window.confirm(`¿Borrar la matricula de ${e.student_name} en ${e.course_name}?`)) return;
    await api.delete(`/enrollments/${e.id}`);
    await loadEnrollments();
  };

  const handleFilter = (value: number | "") => {
    setCourseFilter(value);
    loadEnrollments(value);
  };

  return (
    <div className="page">
      <h1>Matriculas</h1>

      <div className="inline-form">
        {isStaff && (
          <select
            aria-label="Estudiante"
            value={selectedStudent}
            onChange={(e) => setSelectedStudent(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">Selecciona un estudiante...</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.first_name} {s.last_name}
              </option>
            ))}
          </select>
        )}
        <select
          aria-label="Curso"
          value={selectedCourse}
          onChange={(e) => setSelectedCourse(e.target.value === "" ? "" : Number(e.target.value))}
        >
          <option value="">Selecciona un curso...</option>
          {courses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button onClick={handleEnroll} disabled={studentId === null || selectedCourse === ""}>
          {isStudent ? "Matricularme" : "Matricular"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      {isStaff && (
        <div className="inline-form">
          <label htmlFor="course-filter">Filtrar por curso</label>
          <select
            id="course-filter"
            value={courseFilter}
            onChange={(e) => handleFilter(e.target.value === "" ? "" : Number(e.target.value))}
          >
            <option value="">Todos</option>
            {courses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Estudiante</th>
              <th>Curso</th>
              <th>Fecha</th>
              <th>Estado</th>
              {isStaff && <th />}
            </tr>
          </thead>
          <tbody>
            {enrollments.map((e) => (
              <tr key={e.id}>
                <td>{e.id}</td>
                <td>{e.student_name}</td>
                <td>{e.course_name}</td>
                <td>{new Date(e.enrollment_date).toLocaleDateString()}</td>
                <td>
                  {isStaff ? (
                    <select
                      aria-label={`Estado de la matricula ${e.id}`}
                      value={e.status}
                      onChange={(ev) => handleStatus(e.id, ev.target.value as EnrollmentStatus)}
                    >
                      {Object.entries(ENROLLMENT_STATUS_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>
                          {label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    ENROLLMENT_STATUS_LABELS[e.status]
                  )}
                </td>
                {isStaff && (
                  <td>
                    <button className="danger" onClick={() => handleDelete(e)}>
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
