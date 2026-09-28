import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { configDefaults } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    globals: true,
    // Los tests de Playwright (e2e/) se lanzan aparte con npm run test:e2e.
    exclude: [...configDefaults.exclude, "e2e/**"],
  },
});
