import { useEffect, useState, type FormEvent } from "react";
import { api, type Page, type Teacher } from "../api/client";
import { PasswordInput } from "../components/PasswordInput";
import { useAuth } from "../context/AuthContext";

const emptyForm = { email: "", password: "", first_name: "", last_name: "", specialty: "" };

export function Teachers() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Teacher> | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);

  const canCreate = role === "admin";

  const load = async () => {
    const { data } = await api.get<Page<Teacher>>("/teachers", { params: { skip: 0, limit: 50 } });
    setPage(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("/teachers", { ...form, specialty: form.specialty || null });
      setForm(emptyForm);
      await load();
    } catch {
      setError("No se pudo crear el profesor (revisa que el email no exista).");
    }
  };

  const handleDelete = async (id: number) => {
    await api.delete(`/teachers/${id}`);
    await load();
  };

  return (
    <div className="page">
      <h1>Profesores</h1>

      {canCreate && (
        <form className="stacked-form" onSubmit={handleCreate}>
          <input
            placeholder="Email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <PasswordInput
            placeholder="Contrasena (min. 8)"
            minLength={8}
            value={form.password}
            onChange={(password) => setForm({ ...form, password })}
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
          <input
            placeholder="Especialidad"
            value={form.specialty}
            onChange={(e) => setForm({ ...form, specialty: e.target.value })}
          />
          <button type="submit">Crear profesor</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Especialidad</th>
            {canCreate && <th />}
          </tr>
        </thead>
        <tbody>
          {page?.items.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>
                {t.first_name} {t.last_name}
              </td>
              <td>{t.specialty ?? "-"}</td>
              {canCreate && (
                <td>
                  <button onClick={() => handleDelete(t.id)}>Borrar</button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
