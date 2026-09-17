import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { api, type Role } from "../api/client";

interface AuthContextValue {
  token: string | null;
  role: Role | null;
  email: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [role, setRole] = useState<Role | null>(() => localStorage.getItem("role") as Role | null);
  const [email, setEmail] = useState<string | null>(() => localStorage.getItem("email"));

  const login = async (loginEmail: string, password: string) => {
    // El backend usa OAuth2PasswordRequestForm: espera "username", no "email".
    const form = new URLSearchParams();
    form.set("username", loginEmail);
    form.set("password", password);

    const { data } = await api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const me = await api.get("/auth/me", {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", me.data.role);
    localStorage.setItem("email", me.data.email);
    setToken(data.access_token);
    setRole(me.data.role);
    setEmail(me.data.email);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("email");
    setToken(null);
    setRole(null);
    setEmail(null);
  };

  const value = useMemo(
    () => ({ token, role, email, login, logout }),
    [token, role, email]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }
  return ctx;
}
