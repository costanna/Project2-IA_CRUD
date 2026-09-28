# Tablero Kanban — Historias de usuario

Gestion del proyecto con Scrum: 2 sprints de 1 semana (plazo total: 2
semanas). Este documento es la fuente de verdad de las historias de
usuario; se puede importar tal cual a Trello/Jira/GitHub Projects creando
una tarjeta por historia (columna = estado, etiqueta = sprint).

Leyenda de estado: `Backlog` · `Por hacer` · `En progreso` · `En revision` · `Hecho`

## Sprint 1 — Fundacion (dominio, auth, CRUD basico)

| ID | Historia de usuario | Criterios de aceptacion | Puntos | Estado |
|---|---|---|---|---|
| HU-01 | Como **administrador**, quiero registrar profesores y estudiantes para digitalizar las altas del centro. | Los endpoints `POST /students` y `POST /teachers` crean usuario + perfil; email duplicado devuelve 409. | 3 | Hecho |
| HU-02 | Como **usuario**, quiero iniciar sesion con email/contrasena y recibir un token para acceder a la API de forma segura. | `POST /auth/login` devuelve JWT; credenciales invalidas devuelven 401. | 3 | Hecho |
| HU-03 | Como **administrador**, quiero dar de alta cursos con nombre, creditos y profesor asignado. | `POST /courses` valida datos; `teacher_id` opcional. | 2 | Hecho |
| HU-04 | Como **desarrollador**, quiero un modelo de datos relacional (7 tablas) que represente estudiantes, profesores, cursos, horarios, matriculas y notas. | Migraciones de Alembic aplican sin errores sobre PostgreSQL. | 5 | Hecho |
| HU-05 | Como **desarrollador**, quiero tests unitarios e de integracion para cada endpoint critico. | Suite de pytest con >90% de cobertura en `app/`. | 5 | Hecho |
| HU-06 | Como **administrador**, quiero que las credenciales de base de datos y claves secretas se configuren por variables de entorno, no en el codigo. | `.env` fuera de git; `Settings` las lee via pydantic-settings. | 1 | Hecho |

## Sprint 2 — Funcionalidad avanzada y experiencia de usuario

| ID | Historia de usuario | Criterios de aceptacion | Puntos | Estado |
|---|---|---|---|---|
| HU-07 | Como **estudiante**, quiero matricularme en un curso desde la web. | Formulario en `/enrollments`; error claro si ya estoy matriculado (409). | 3 | Hecho |
| HU-08 | Como **profesor**, quiero registrar notas de mis estudiantes y que se enteren al instante. | `POST /grades` + notificacion por WebSocket al estudiante conectado. | 5 | Hecho |
| HU-09 | Como **administrador**, quiero exportar el listado de estudiantes y cursos a CSV para reportes externos. | Boton "Exportar CSV" en el frontend; endpoint `/export` en ambos recursos. | 2 | Hecho |
| HU-10 | Como **usuario de la API**, quiero listados paginados y filtrables (por curso/profesor) para no descargar todo el dataset. | `skip`/`limit` + filtros `teacher_id`, `course_id`, `student_id`, `enrollment_id`. | 3 | Hecho |
| HU-11 | Como **administrador**, quiero que los listados de cursos respondan rapido aunque haya muchas peticiones repetidas. | Cache en memoria con invalidacion automatica al crear/editar/borrar. | 2 | Hecho |
| HU-12 | Como **responsable tecnico**, quiero que cada cambio a `main` pase tests y linters automaticamente antes de fusionarse. | Pipeline de GitHub Actions (backend + frontend) en verde. | 3 | Hecho |
| HU-13 | Como **cliente**, quiero una interfaz web sencilla para no depender de Swagger para el uso diario. | SPA en React con login, cursos, estudiantes, matriculas y notas. | 5 | Hecho |
| HU-14 | Como **responsable tecnico**, quiero poder desplegar todo el stack (API + BD + frontend) con un solo comando. | `docker-compose up` levanta Postgres, backend y frontend enlazados. | 3 | Hecho |

## Backlog (fuera de alcance de las 2 semanas, futuras iteraciones)

| ID | Historia de usuario | Motivo de posponer |
|---|---|---|
| HU-15 | Como **profesor**, quiero editar mi propio horario de clases desde la web. | UI de horarios no priorizada frente a matriculas/notas. |
| HU-16 | Como **administrador**, quiero un panel de estadisticas (notas medias, ocupacion de cursos). | Requiere disenar agregaciones adicionales; no bloquea el MVP. |
| HU-17 | Como **usuario**, quiero recuperar mi contrasena por email. | Requiere integracion con un proveedor de email externo. |

## Como importar este tablero a una herramienta visual

- **Trello**: Power-Up "CSV Import" o crear manualmente una lista por
  sprint y una tarjeta por fila, copiando la columna "Historia de usuario"
  al titulo y los criterios de aceptacion a la descripcion.
- **GitHub Projects**: cada fila puede convertirse en un Issue (usar
  `gh issue create --title "HU-XX: ..." --body "..."`) y añadirse al
  proyecto con el estado correspondiente.
