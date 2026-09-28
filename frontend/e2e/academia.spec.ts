import { expect, test } from "@playwright/test";
import { ADMIN, API_URL, ensureAdmin, login, uniqueSuffix } from "./helpers";

test.beforeAll(async () => {
  await ensureAdmin();
});

test("login incorrecto muestra un error", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(ADMIN.email);
  await page.getByLabel("Contrasena").fill("contrasena-mala");
  await page.getByRole("button", { name: "Entrar" }).click();

  await expect(page.getByText("Email o contrasena incorrectos.")).toBeVisible();
});

test("flujo completo: profesor, curso, estudiante, matricula y nota", async ({ page, browser }) => {
  const id = uniqueSuffix();
  const teacherEmail = `profe-${id}@e2e.dev`;
  const studentEmail = `alumno-${id}@e2e.dev`;
  const courseName = `Curso E2E ${id}`;
  const teacherName = `Laura Garcia${id}`;
  const studentName = `Ana Ruiz${id}`;

  await login(page, ADMIN.email, ADMIN.password);

  // 1. Alta de profesor
  await page.getByRole("link", { name: "Profesores" }).click();
  await page.getByPlaceholder("Email").fill(teacherEmail);
  await page.getByPlaceholder("Contrasena (min. 8)").fill("profe1234");
  await page.getByPlaceholder("Nombre").fill("Laura");
  await page.getByPlaceholder("Apellidos").fill(`Garcia${id}`);
  await page.getByPlaceholder("Especialidad").fill("Web");
  await page.getByRole("button", { name: "Crear profesor" }).click();
  await expect(page.getByRole("cell", { name: teacherEmail })).toBeVisible();

  // 2. Curso asignado a ese profesor
  await page.getByRole("link", { name: "Cursos" }).click();
  await page.getByPlaceholder("Nombre del curso").fill(courseName);
  await page.getByLabel("Profesor").selectOption({ label: teacherName });
  await page.getByRole("button", { name: "Crear curso" }).click();
  await expect(page.getByRole("row", { name: new RegExp(courseName) })).toContainText(teacherName);

  // 3. Alta de estudiante y edicion de su telefono
  await page.getByRole("link", { name: "Estudiantes" }).click();
  await page.getByPlaceholder("Email").fill(studentEmail);
  await page.getByPlaceholder("Contrasena (min. 8)").fill("alumno1234");
  await page.getByPlaceholder("Nombre").fill("Ana");
  await page.getByPlaceholder("Apellidos").fill(`Ruiz${id}`);
  await page.getByRole("button", { name: "Crear estudiante" }).click();
  await page.getByRole("row", { name: new RegExp(studentEmail) }).getByRole("button", { name: "Editar" }).click();
  await page.getByRole("cell").getByLabel("Telefono").fill("600111222");
  await page.getByRole("button", { name: "Guardar" }).click();
  await expect(page.getByRole("row", { name: new RegExp(studentEmail) })).toContainText("600111222");

  // 4. El admin matricula al estudiante
  await page.getByRole("link", { name: "Matriculas" }).click();
  await page.getByLabel("Estudiante").selectOption({ label: studentName });
  await page.getByLabel("Curso", { exact: true }).selectOption({ label: courseName });
  await page.getByRole("button", { name: "Matricular" }).click();
  await expect(page.getByRole("row", { name: new RegExp(studentName) })).toContainText(courseName);

  // 5. El profesor pone una nota
  const teacherContext = await browser.newContext();
  const teacherPage = await teacherContext.newPage();
  await login(teacherPage, teacherEmail, "profe1234");
  await teacherPage.getByRole("link", { name: "Notas" }).click();
  await teacherPage.getByLabel("Matricula").selectOption({ label: `${studentName} · ${courseName}` });
  await teacherPage.getByPlaceholder("Evaluacion (ej. Parcial 1)").fill("Parcial 1");
  await teacherPage.getByLabel("Nota").fill("8.5");
  await teacherPage.getByRole("button", { name: "Registrar nota" }).click();
  await expect(teacherPage.getByRole("cell", { name: "Parcial 1" })).toBeVisible();
  await teacherContext.close();

  // 6. El estudiante ve su nota, sin opciones de gestion
  const studentContext = await browser.newContext();
  const studentPage = await studentContext.newPage();
  await login(studentPage, studentEmail, "alumno1234");
  await expect(studentPage.getByRole("link", { name: "Estudiantes" })).toHaveCount(0);
  await studentPage.getByRole("link", { name: "Notas" }).click();
  await studentPage.getByLabel("Matricula").selectOption({ label: `${studentName} · ${courseName}` });
  await expect(studentPage.getByRole("cell", { name: "8.5" })).toBeVisible();
  await expect(studentPage.getByRole("button", { name: "Registrar nota" })).toHaveCount(0);
  await studentContext.close();
});

test("un estudiante no puede entrar en la gestion de estudiantes", async ({ page, request }) => {
  const email = `solo-${uniqueSuffix()}@e2e.dev`;
  const register = await request.post(`${API_URL}/auth/register`, {
    data: { email, password: "alumno1234" },
  });
  expect(register.status()).toBe(201);

  await login(page, email, "alumno1234");
  await page.goto("/students");

  await expect(page).toHaveURL(/\/dashboard$/);
});
