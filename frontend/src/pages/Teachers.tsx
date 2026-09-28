import { useEffect, useState, type FormEvent } from "react";
import { api, type Page, type Teacher } from "../api/client";
import { PasswordInput } from "../components/PasswordInput";
import { useAuth } from "../context/AuthContext";

const emptyForm = { email: "", password: "", first_name: "", last_name: "", specialty: "" };

interface EditState {
  id: number;
  first_name: string;
  last_name: string;
  specialty: string;
}

export function Teachers() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Teacher> | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState<EditState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canManage = role === "admin";

  const load = async () => {
    const { data } = await api.get<Page<Teacher>>("/teachers", { params: { skip: 0, limit: 100 } });
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

  const handleSave = async () => {
    if (!editing) return;
    setError(null);
    try {
      await api.put(`/teachers/${editing.id}`, {
        first_name: editing.first_name,
        last_name: editing.last_name,
        specialty: editing.specialty || null,
      });
      setEditing(null);
      await load();
    } catch {
      setError("No se pudieron guardar los cambios.");
    }
  };

  const handleDelete = async (t: Teacher) => {
    if (!window.confirm(`¿Borrar a ${t.first_name} ${t.last_name}? Sus cursos quedaran sin profesor.`)) return;
    await api.delete(`/teachers/${t.id}`);
    await load();
  };

  return (
    <div className="page">
      <h1>Profesores</h1>

      {canManage && (
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

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Apellidos</th>
              <th>Email</th>
              <th>Especialidad</th>
              {canManage && <th />}
            </tr>
          </thead>
          <tbody>
            {page?.items.map((t) =>
              editing?.id === t.id ? (
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td>
                    <input
                      aria-label="Nombre"
                      value={editing.first_name}
                      onChange={(e) => setEditing({ ...editing, first_name: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      aria-label="Apellidos"
                      value={editing.last_name}
                      onChange={(e) => setEditing({ ...editing, last_name: e.target.value })}
                    />
                  </td>
                  <td>{t.email}</td>
                  <td>
                    <input
                      aria-label="Especialidad"
                      value={editing.specialty}
                      onChange={(e) => setEditing({ ...editing, specialty: e.target.value })}
                    />
                  </td>
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
                <tr key={t.id}>
                  <td>{t.id}</td>
                  <td>{t.first_name}</td>
                  <td>{t.last_name}</td>
                  <td>{t.email}</td>
                  <td>{t.specialty ?? "-"}</td>
                  {canManage && (
                    <td>
                      <div className="row-actions">
                        <button
                          className="secondary"
                          onClick={() =>
                            setEditing({
                              id: t.id,
                              first_name: t.first_name,
                              last_name: t.last_name,
                              specialty: t.specialty ?? "",
                            })
                          }
                        >
                          Editar
                        </button>
                        <button className="danger" onClick={() => handleDelete(t)}>
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
