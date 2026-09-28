import { useEffect, useState, type FormEvent } from "react";
import { api, type Page, type Student } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function Students() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Student> | null>(null);
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState<string | null>(null);

  const canCreate = role === "admin";

  const load = async () => {
    const { data } = await api.get<Page<Student>>("/students", { params: { skip: 0, limit: 50 } });
    setPage(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("/students", form);
      setForm({ email: "", password: "", first_name: "", last_name: "" });
      await load();
    } catch {
      setError("No se pudo crear el estudiante (revisa que el email no exista).");
    }
  };

  const handleDelete = async (id: number) => {
    await api.delete(`/students/${id}`);
    await load();
  };

  return (
    <div className="page">
      <h1>Estudiantes</h1>

      {canCreate && (
        <form className="stacked-form" onSubmit={handleCreate}>
          <input
            placeholder="Email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <input
            placeholder="Contrasena"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <input
            placeholder="Nombre"
            required
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
          />
          <input
            placeholder="Apellidos"
            required
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
          />
          <button type="submit">Crear estudiante</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Telefono</th>
            {canCreate && <th />}
          </tr>
        </thead>
        <tbody>
          {page?.items.map((s) => (
            <tr key={s.id}>
              <td>{s.id}</td>
              <td>
                {s.first_name} {s.last_name}
              </td>
              <td>{s.phone ?? "-"}</td>
              {canCreate && (
                <td>
                  <button onClick={() => handleDelete(s.id)}>Borrar</button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
