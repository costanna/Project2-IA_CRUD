import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Navbar() {
  const { email, role, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar__brand">🎓 Academia F5</div>
      <div className="navbar__links">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/courses">Cursos</NavLink>
        {(role === "admin" || role === "teacher") && <NavLink to="/students">Estudiantes</NavLink>}
        {(role === "admin" || role === "teacher") && <NavLink to="/teachers">Profesores</NavLink>}
        <NavLink to="/enrollments">Matriculas</NavLink>
        <NavLink to="/grades">Notas</NavLink>
      </div>
      <div className="navbar__user">
        <span>
          {email} <em>({role})</em>
        </span>
        <button onClick={handleLogout}>Salir</button>
      </div>
    </nav>
  );
}
