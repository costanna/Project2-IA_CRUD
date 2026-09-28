import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Courses } from "./Courses";
import { Enrollments } from "./Enrollments";
import { Students } from "./Students";

const mockApi = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}));

const mockAuth = vi.hoisted(() => ({ role: "admin" as string }));

vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  api: mockApi,
}));

vi.mock("../context/AuthContext", () => ({
  useAuth: () => mockAuth,
}));

const page = <T,>(items: T[]) => ({ data: { items, total: items.length, skip: 0, limit: 100 } });

const ana = {
  id: 1,
  user_id: 10,
  email: "ana@academiaf5.com",
  first_name: "Ana",
  last_name: "Ruiz",
  birth_date: null,
  phone: null,
  enrollment_date: "2026-09-01T00:00:00",
};
const laura = {
  id: 7,
  user_id: 20,
  email: "laura@academiaf5.com",
  first_name: "Laura",
  last_name: "Garcia",
  specialty: "Web",
  hire_date: "2026-09-01T00:00:00",
};
const react = { id: 3, name: "React", description: null, credits: 4, teacher_id: null };

function routeGet(routes: Record<string, unknown[]>) {
  mockApi.get.mockImplementation((url: string) => Promise.resolve(page(routes[url] ?? [])));
}

beforeEach(() => {
  vi.clearAllMocks();
  mockAuth.role = "admin";
  mockApi.post.mockResolvedValue({ data: {} });
  mockApi.put.mockResolvedValue({ data: {} });
});

describe("Students", () => {
  it("permite editar un estudiante desde la tabla", async () => {
    routeGet({ "/students": [ana] });
    render(<Students />);

    fireEvent.click(await screen.findByRole("button", { name: "Editar" }));
    const row = screen.getByDisplayValue("Ana").closest("tr")!;
    fireEvent.change(within(row).getByLabelText("Telefono"), { target: { value: "600111222" } });
    fireEvent.click(within(row).getByRole("button", { name: "Guardar" }));

    await waitFor(() =>
      expect(mockApi.put).toHaveBeenCalledWith("/students/1", {
        first_name: "Ana",
        last_name: "Ruiz",
        phone: "600111222",
        birth_date: null,
      })
    );
  });

  it("muestra el email y oculta las acciones a los profesores", async () => {
    mockAuth.role = "teacher";
    routeGet({ "/students": [ana] });
    render(<Students />);

    expect(await screen.findByText("ana@academiaf5.com")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
  });
});

describe("Courses", () => {
  it("muestra el nombre del profesor y permite asignarlo al editar", async () => {
    routeGet({ "/courses": [{ ...react, teacher_id: null }], "/teachers": [laura] });
    render(<Courses />);

    expect(await screen.findByText("Sin asignar")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    const row = screen.getByDisplayValue("React").closest("tr")!;
    fireEvent.change(within(row).getByLabelText("Profesor"), { target: { value: "7" } });
    fireEvent.click(within(row).getByRole("button", { name: "Guardar" }));

    await waitFor(() =>
      expect(mockApi.put).toHaveBeenCalledWith("/courses/3", {
        name: "React",
        description: null,
        credits: 4,
        teacher_id: 7,
      })
    );
  });
});

describe("Enrollments", () => {
  it("un admin matricula a un estudiante en un curso", async () => {
    routeGet({ "/courses": [react], "/students": [ana], "/enrollments": [] });
    render(<Enrollments />);

    const studentSelect = await screen.findByLabelText("Estudiante");
    await screen.findByRole("option", { name: "Ana Ruiz" });
    fireEvent.change(studentSelect, { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Curso"), { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "Matricular" }));

    await waitFor(() =>
      expect(mockApi.post).toHaveBeenCalledWith("/enrollments", { student_id: 1, course_id: 3 })
    );
  });

  it("muestra nombres en lugar de ids", async () => {
    routeGet({
      "/courses": [react],
      "/students": [ana],
      "/enrollments": [
        {
          id: 5,
          student_id: 1,
          course_id: 3,
          enrollment_date: "2026-09-10T00:00:00",
          status: "active",
          student_name: "Ana Ruiz",
          course_name: "React",
        },
      ],
    });
    render(<Enrollments />);

    const row = (await screen.findByText("Ana Ruiz", { selector: "td" })).closest("tr")!;
    expect(within(row).getByText("React")).toBeInTheDocument();
  });
});
