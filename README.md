# 🎓 Academia F5 — Sistema de Gestión Académica

![Banner Proyectos](https://github.com/user-attachments/assets/94ecebe4-ceba-47ae-8f3c-af14bdfe8606)

## 📋 Planteamiento

Eres parte de un equipo de desarrollo en una consultora tecnológica especializada en soluciones para pequeñas y medianas empresas. Un centro educativo necesita digitalizar y optimizar la gestión de estudiantes, profesores, cursos, matrículas y notas, reemplazando hojas de cálculo manuales.

Este repositorio implementa esa solución: una **API REST** (FastAPI + PostgreSQL) y un **frontend web** (React + TypeScript) para gestionar el día a día de la academia.

## 🧱 Stack técnico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic |
| Base de datos | PostgreSQL (producción) / SQLite (tests) |
| Autenticación | JWT (`python-jose`) + roles (`admin`, `teacher`, `student`) |
| Tiempo real | WebSockets (notificación de notas nuevas) |
| Servicios externos | Resend (email al estudiante cuando recibe una nota) |
| Frontend | React 18 + TypeScript + Vite + React Router |
| Tests | pytest (unit + integración, 97% cobertura), Vitest + Testing Library, Playwright (end-to-end) |
| Calidad de código | black, isort, flake8, pre-commit |
| CI/CD | GitHub Actions (lint + tests con PostgreSQL real, build de frontend, tests end-to-end) |
| Contenerización | Docker + docker-compose (db + backend + frontend) |

## 🗂️ Estructura del repositorio

```
backend/          API REST (FastAPI) — ver backend/app/
  app/
    core/         configuración, seguridad (JWT), cache, logging
    models/       entidades SQLAlchemy (7 tablas)
    schemas/      DTOs Pydantic (entrada/salida de la API)
    repositories/ acceso a datos (patrón Repository)
    services/     lógica de negocio
    routers/      endpoints REST + WebSocket
  alembic/        migraciones de base de datos
  tests/          unit/ e integration/
  e2e_server.py   arranca la API para los tests end-to-end
frontend/         SPA React + Vite que consume la API
  e2e/            tests end-to-end (Playwright)
docs/             diagrama ER, documentación de API, Kanban, retrospectiva, ADRs
.github/workflows/ci.yml   pipeline de CI
docker-compose.yml         levanta todo el stack con un comando
```

## 🎯 Objetivo

Desarrollar una API REST y una base de datos SQL que permitan gestionar eficientemente la academia, preparando el sistema para crecer (más cursos, más usuarios, más funcionalidades).

## 🚀 Puesta en marcha

### Opción A — Docker (recomendado, levanta todo el stack)

```bash
cp .env.example .env         # ajusta SECRET_KEY si quieres
docker compose up --build
```

- API: http://localhost:8000/docs (Swagger)
- Frontend: http://localhost:8080

### Opción C — Nube (Neon + Render + Vercel)

Para una demo o presentación sin depender de tu máquina: guía paso a paso
en [docs/deployment.md](docs/deployment.md).

### Opción B — Desarrollo local (backend)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows (usa `source .venv/bin/activate` en Linux/Mac)
pip install -r requirements.txt
cp .env.example .env          # por defecto usa SQLite, no requiere Postgres
alembic upgrade head          # aplica las migraciones
uvicorn app.main:app --reload
```

### Opción B — Desarrollo local (frontend)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev                   # http://localhost:5173
```

### Ejecutar los tests

```bash
# Backend: unitarios + integración (SQLite temporal, no requiere Postgres)
cd backend
pip install -r requirements-dev.txt
pytest

# Frontend: tests de componentes
cd frontend
npm run test

# End-to-end: levanta API + frontend reales y los recorre con Chromium
cd frontend
npx playwright install chromium   # solo la primera vez
npm run test:e2e
```

### Linting y formateo

```bash
cd backend
black app tests && isort app tests && flake8 app tests
```

O instala los hooks de pre-commit (raíz del repo) para que se ejecuten automáticamente en cada commit:

```bash
pip install -r backend/requirements-dev.txt
pre-commit install
```

## 🔑 Primeros pasos con la API

1. Regístrate como admin: `POST /api/v1/auth/register` con `{"email": "...", "password": "...", "role": "admin"}`. Solo la primera cuenta puede crearse así; las siguientes cuentas de admin o profesor las crea un admin.
2. Inicia sesión: `POST /api/v1/auth/login` (form `username`/`password`) → devuelve un JWT.
3. Usa el botón **Authorize** de Swagger (`/docs`) con `Bearer <token>` para probar el resto de endpoints.

Detalle completo de endpoints, roles y códigos de error en [docs/api.md](docs/api.md).

## 📦 Entregables

| Entregable | Dónde encontrarlo |
|---|---|
| Diagrama ER de la base de datos | [docs/er-diagram.md](docs/er-diagram.md) |
| Repositorio en GitHub con código fuente | este repositorio |
| Documentación de la API (Swagger) | `/docs` en el servidor + [docs/api.md](docs/api.md) |
| Suite de tests completa y pasando | `backend/tests/` (79 tests, 97% cobertura) + `frontend/src/**/*.test.tsx` (12 tests) + `frontend/e2e/` (3 escenarios Playwright) |
| Documento de retrospectiva | [docs/retrospective.md](docs/retrospective.md) |
| Tablero Kanban con historias de usuario | [docs/kanban.md](docs/kanban.md) |
| Gestión de equipo / roles / ceremonias | [docs/team.md](docs/team.md) |
| Decisiones de arquitectura | [docs/adr/](docs/adr/) |
| Guía de despliegue en la nube | [docs/deployment.md](docs/deployment.md) |

## 🏆 Niveles de entrega cubiertos

- **🟢 Esencial**: 7 tablas relacionadas · CRUD completo · tests unitarios por endpoint · Markdown · Kanban · variables de entorno · logging básico · manejo de excepciones.
- **🟡 Medio**: 7 tablas (>5) · Swagger interactivo · errores HTTP semánticos (401/403/404/409/422/500) · exportación a CSV (estudiantes y cursos) · paginación y filtrado en los GET.
- **🟠 Avanzado**: JWT + roles (admin/teacher/student) con control de propiedad (un estudiante solo accede a sus datos) · caché en memoria con invalidación automática · WebSocket de notificaciones en tiempo real.
- **🔴 Experto**: Docker + docker-compose (API + PostgreSQL + frontend) · interfaz de usuario (SPA en React) · **despliegue real en la nube** (Neon + Render + Vercel, ver [docs/deployment.md](docs/deployment.md)) · **integración con un servicio externo** (emails de notas con Resend).

## 🌟 Competencias demostradas

- **Diseñar y gestionar bases de datos**: modelo relacional de 7 tablas con relaciones 1:1, 1:N y N:M, migraciones versionadas con Alembic (verificadas contra PostgreSQL real, en local y en Neon), restricciones de integridad (`UNIQUE`, `ON DELETE CASCADE/SET NULL`). Ver [docs/er-diagram.md](docs/er-diagram.md).
- **Back-end de aplicaciones**: API REST en capas (routers → services → repositories → models), JWT + RBAC, caché, WebSockets. Ver [docs/adr/](docs/adr/).
- **Implementar tests de calidad**: 79 tests de backend (97% de cobertura, incluidos tests de permisos y del servicio de email con transporte simulado), 12 tests de frontend (Vitest + Testing Library) y 3 escenarios end-to-end con Playwright; todo se ejecuta en CI.
- **Gestionar equipos técnicos**: roles, ceremonias Scrum y comunicación documentados en [docs/team.md](docs/team.md).
- **Configura y automatiza su entorno de trabajo**: pre-commit, CI/CD, `.editorconfig`, configuración de VS Code, y uso de IA (Claude Code) como asistente de desarrollo (documentado en [docs/team.md](docs/team.md)).
- **Despliegue de aplicaciones**: Docker multi-servicio con `docker-compose` (verificado de extremo a extremo) y despliegue en la nube con Neon + Render + Vercel ([docs/deployment.md](docs/deployment.md)).
- **Desarrollo de interfaces dinámicas**: SPA en React con CRUD completo (edición en línea en todas las tablas), rutas protegidas por rol, relaciones por nombre (profesor de un curso, matrículas), paginación, filtros, exportación CSV y notificaciones en tiempo real vía WebSocket.
- **Fundamentos, patrones y calidad de código**: patrón Repository, inyección de dependencias, DTOs con Pydantic, linters automatizados. Ver [docs/adr/0001-arquitectura-en-capas.md](docs/adr/0001-arquitectura-en-capas.md).

## 📅 Plazos

Dos semanas (2 sprints de 1 semana) más un sprint corto de cierre tras la demo — ver [docs/kanban.md](docs/kanban.md).
