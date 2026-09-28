import { defineConfig, devices } from "@playwright/test";

// Tests end-to-end: levantan la API real (SQLite temporal) y el frontend
// (Vite) y recorren los flujos principales en un navegador de verdad.
export const API_PORT = 8001;
export const WEB_PORT = 5174;
export const API_URL = `http://localhost:${API_PORT}/api/v1`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://localhost:${WEB_PORT}`,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      // Base de datos nueva en cada ejecucion (ver backend/e2e_server.py).
      command: `python e2e_server.py ${API_PORT}`,
      cwd: "../backend",
      url: `http://localhost:${API_PORT}/health`,
      reuseExistingServer: false,
      timeout: 60_000,
      env: {
        DATABASE_URL: "sqlite:///./e2e.db",
        SECRET_KEY: "e2e-secret-key",
        CORS_ORIGINS: `http://localhost:${WEB_PORT}`,
        RESEND_API_KEY: "",
      },
    },
    {
      command: `npx vite --port ${WEB_PORT} --strictPort`,
      url: `http://localhost:${WEB_PORT}`,
      reuseExistingServer: false,
      timeout: 60_000,
      env: {
        VITE_API_URL: API_URL,
        VITE_WS_URL: `ws://localhost:${API_PORT}/ws/notifications`,
      },
    },
  ],
});
