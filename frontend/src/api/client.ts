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

// Si el token expira o es invalido, forzamos vuelta al login.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
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

export interface Student {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  birth_date: string | null;
  phone: string | null;
  enrollment_date: string;
}

export interface Teacher {
  id: number;
  user_id: number;
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
  status: "active" | "completed" | "dropped";
}

export interface Grade {
  id: number;
  enrollment_id: number;
  evaluation_name: string;
  score: number;
  date: string;
}
