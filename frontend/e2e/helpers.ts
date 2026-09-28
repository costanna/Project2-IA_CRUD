import { expect, request, type Page } from "@playwright/test";
import { API_URL } from "../playwright.config";

export { API_URL };

export const ADMIN = { email: "admin@e2e.dev", password: "admin1234" };

// La primera cuenta del sistema puede registrarse como admin (arranque
// inicial). Si ya existe, la API responde 409 y se ignora.
export async function ensureAdmin() {
  const api = await request.newContext();
  const response = await api.post(`${API_URL}/auth/register`, { data: { ...ADMIN, role: "admin" } });
  expect([201, 409]).toContain(response.status());
  await api.dispose();
}

export async function login(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Contrasena").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

export function uniqueSuffix() {
  return Date.now().toString(36);
}
