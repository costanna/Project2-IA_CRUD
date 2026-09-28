import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL: API_URL });

// Adjunta el JWT guardado tras el login a cada peticion saliente.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Si el token expira o es invalido, forzamos vuelta al login. Un 401 del
// propio login (credenciales incorrectas) lo gestiona la pantalla de login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes("/auth/login");
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export type Role = "admin" | "teacher" | "student";

export interface Page<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// Descarga un endpoint CSV de la API como fichero (usa el JWT del interceptor).
export async function downloadCsv(path: string, filename: string) {
  const response = await api.get(path, { responseType: "blob" });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export interface Student {
  id: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  birth_date: string | null;
  phone: string | null;
  enrollment_date: string;
}

export interface Teacher {
  id: number;
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  specialty: string | null;
  hire_date: string;
}

export interface Course {
  id: number;
  name: string;
  description: string | null;
  credits: number;
  teacher_id: number | null;
}

export interface Enrollment {
  id: number;
  student_id: number;
  course_id: number;
  enrollment_date: string;
  status: EnrollmentStatus;
  student_name: string;
  course_name: string;
}

export type EnrollmentStatus = "active" | "completed" | "dropped";

export const ENROLLMENT_STATUS_LABELS: Record<EnrollmentStatus, string> = {
  active: "Activa",
  completed: "Completada",
  dropped: "Baja",
};

export type DayOfWeek =
  | "monday"
  | "tuesday"
  | "wednesday"
  | "thursday"
  | "friday"
  | "saturday"
  | "sunday";

export const DAY_LABELS: Record<DayOfWeek, string> = {
  monday: "Lunes",
  tuesday: "Martes",
  wednesday: "Miercoles",
  thursday: "Jueves",
  friday: "Viernes",
  saturday: "Sabado",
  sunday: "Domingo",
};

export interface Schedule {
  id: number;
  course_id: number;
  day_of_week: DayOfWeek;
  start_time: string;
  end_time: string;
  classroom: string | null;
}

export interface Grade {
  id: number;
  enrollment_id: number;
  evaluation_name: string;
  score: number;
  date: string;
}
