import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "./ProtectedRoute";

const mockAuth = vi.hoisted(() => ({
  token: null as string | null,
  role: null as string | null,
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockAuth,
}));

function renderWithRoute() {
  return render(
    <MemoryRouter initialEntries={["/private"]}>
      <Routes>
        <Route path="/login" element={<div>Pantalla de login</div>} />
        <Route path="/dashboard" element={<div>Pantalla de dashboard</div>} />
        <Route
          path="/private"
          element={
            <ProtectedRoute roles={["admin"]}>
              <div>Contenido privado</div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  it("redirige a /login si no hay token", () => {
    mockAuth.token = null;
    mockAuth.role = null;

    renderWithRoute();

    expect(screen.getByText("Pantalla de login")).toBeInTheDocument();
  });

  it("redirige a /dashboard si el rol no esta autorizado", () => {
    mockAuth.token = "fake-token";
    mockAuth.role = "student";

    renderWithRoute();

    expect(screen.getByText("Pantalla de dashboard")).toBeInTheDocument();
  });

  it("renderiza el contenido si el usuario esta autenticado y autorizado", () => {
    mockAuth.token = "fake-token";
    mockAuth.role = "admin";

    renderWithRoute();

    expect(screen.getByText("Contenido privado")).toBeInTheDocument();
  });
});
