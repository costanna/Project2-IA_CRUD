import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { Login } from "./Login";

const loginMock = vi.fn();

vi.mock("../context/AuthContext", () => ({
  useAuth: () => ({ login: loginMock, token: null, role: null, email: null, logout: vi.fn() }),
}));

function renderLogin() {
  return render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );
}

describe("Login", () => {
  it("muestra los campos de email y contrasena", () => {
    renderLogin();

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contrasena/i)).toBeInTheDocument();
  });

  it("llama a login con las credenciales introducidas al enviar el formulario", async () => {
    loginMock.mockResolvedValueOnce(undefined);
    renderLogin();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "admin@academiaf5.dev" } });
    fireEvent.change(screen.getByLabelText(/contrasena/i), { target: { value: "clave12345" } });
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    await waitFor(() =>
      expect(loginMock).toHaveBeenCalledWith("admin@academiaf5.dev", "clave12345")
    );
  });

  it("muestra un mensaje de error cuando el login falla", async () => {
    loginMock.mockRejectedValueOnce(new Error("credenciales invalidas"));
    renderLogin();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "malo@academiaf5.dev" } });
    fireEvent.change(screen.getByLabelText(/contrasena/i), { target: { value: "incorrecta" } });
    fireEvent.click(screen.getByRole("button", { name: /entrar/i }));

    expect(await screen.findByText(/incorrectos/i)).toBeInTheDocument();
  });
});
