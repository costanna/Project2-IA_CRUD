import { useEffect, useState, type FormEvent } from "react";
import { api, downloadCsv, type Page, type Student } from "../api/client";
import { PasswordInput } from "../components/PasswordInput";
import { useAuth } from "../context/AuthContext";

const emptyForm = { email: "", password: "", first_name: "", last_name: "", phone: "", birth_date: "" };

interface EditState {
  id: number;
  first_name: string;
  last_name: string;
  phone: string;
  birth_date: string;
}

export function Students() {
  const { role } = useAuth();
  const [page, setPage] = useState<Page<Student> | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState<EditState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canManage = role === "admin";

  const load = async () => {
    const { data } = await api.get<Page<Student>>("/students", { params: { skip: 0, limit: 100 } });
    setPage(data);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await api.post("/students", {
        ...form,
        phone: form.phone || null,
        birth_date: form.birth_date || null,
      });
      setForm(emptyForm);
      await load();
    } catch {
      setError("No se pudo crear el estudiante (revisa que el email no exista).");
    }
  };

  const startEdit = (s: Student) =>
    setEditing({
      id: s.id,
      first_name: s.first_name,
      last_name: s.last_name,
      phone: s.phone ?? "",
      birth_date: s.birth_date ?? "",
    });

  const handleSave = async () => {
    if (!editing) return;
    setError(null);
    try {
      await api.put(`/students/${editing.id}`, {
        first_name: editing.first_name,
        last_name: editing.last_name,
        phone: editing.phone || null,
        birth_date: editing.birth_date || null,
      });
      setEditing(null);
      await load();
    } catch {
      setError("No se pudieron guardar los cambios.");
    }
  };

  const handleDelete = async (s: Student) => {
    if (!window.confirm(`¿Borrar a ${s.first_name} ${s.last_name}? Se eliminara tambien su cuenta.`)) return;
    await api.delete(`/students/${s.id}`);
    await load();
  };

  return (
    <div className="page">
      <div className="toolbar">
        <h1>Estudiantes</h1>
        <button className="secondary" onClick={() => downloadCsv("/students/export", "students.csv")}>
          Exportar CSV
        </button>
      </div>

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
            placeholder="Telefono"
            value={form.phone}
            onChange={(e) => setForm({ ...form, phone: e.target.value })}
          />
          <input
            type="date"
            aria-label="Fecha de nacimiento"
            value={form.birth_date}
            onChange={(e) => setForm({ ...form, birth_date: e.target.value })}
          />
          <button type="submit">Crear estudiante</button>
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
              <th>Telefono</th>
              <th>Nacimiento</th>
              {canManage && <th />}
            </tr>
          </thead>
          <tbody>
            {page?.items.map((s) =>
              editing?.id === s.id ? (
                <tr key={s.id}>
                  <td>{s.id}</td>
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
                  <td>{s.email}</td>
                  <td>
                    <input
                      aria-label="Telefono"
                      value={editing.phone}
                      onChange={(e) => setEditing({ ...editing, phone: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      type="date"
                      aria-label="Fecha de nacimiento"
                      value={editing.birth_date}
                      onChange={(e) => setEditing({ ...editing, birth_date: e.target.value })}
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
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.first_name}</td>
                  <td>{s.last_name}</td>
                  <td>{s.email}</td>
                  <td>{s.phone ?? "-"}</td>
                  <td>{s.birth_date ?? "-"}</td>
                  {canManage && (
                    <td>
                      <div className="row-actions">
                        <button className="secondary" onClick={() => startEdit(s)}>
                          Editar
                        </button>
                        <button className="danger" onClick={() => handleDelete(s)}>
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
