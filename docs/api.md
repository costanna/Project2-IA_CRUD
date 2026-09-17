# Documentacion de la API

La documentacion interactiva (Swagger UI) se genera automaticamente por
FastAPI y esta disponible en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

Con el servidor levantado (ver [README](../README.md)) puedes probar todos
los endpoints desde ahi, incluyendo el flujo de login (boton "Authorize").

## Resumen de endpoints

Todos los endpoints (salvo `/health`, `/auth/register` y `/auth/login`)
requieren cabecera `Authorization: Bearer <token>`.

| Recurso | Metodo y ruta | Roles permitidos | Descripcion |
|---|---|---|---|
| Auth | `POST /api/v1/auth/register` | publico | Crea una cuenta (rol `student` por defecto) |
| Auth | `POST /api/v1/auth/login` | publico | Devuelve un JWT (`OAuth2PasswordRequestForm`) |
| Auth | `GET /api/v1/auth/me` | cualquiera autenticado | Perfil del usuario autenticado |
| Estudiantes | `GET /api/v1/students` | admin, teacher | Lista paginada |
| Estudiantes | `GET /api/v1/students/me` | student | Mi propio perfil de estudiante |
| Estudiantes | `GET /api/v1/students/export` | admin, teacher | Exporta CSV |
| Estudiantes | `GET /api/v1/students/{id}` | admin, teacher | Detalle |
| Estudiantes | `POST /api/v1/students` | admin | Alta (crea `User` + `Student`) |
| Estudiantes | `PUT /api/v1/students/{id}` | admin | Actualizacion parcial |
| Estudiantes | `DELETE /api/v1/students/{id}` | admin | Baja |
| Profesores | `GET /api/v1/teachers` | cualquiera autenticado | Lista paginada |
| Profesores | `POST /api/v1/teachers` | admin | Alta |
| Profesores | `PUT /api/v1/teachers/{id}` | admin | Actualizacion |
| Profesores | `DELETE /api/v1/teachers/{id}` | admin | Baja |
| Cursos | `GET /api/v1/courses` | cualquiera autenticado | Lista paginada, filtro `teacher_id`, cacheada |
| Cursos | `GET /api/v1/courses/export` | admin | Exporta CSV |
| Cursos | `POST /api/v1/courses` | admin | Alta |
| Cursos | `PUT /api/v1/courses/{id}` | admin | Actualizacion (invalida cache) |
| Cursos | `DELETE /api/v1/courses/{id}` | admin | Baja (invalida cache) |
| Horarios | `GET /api/v1/schedules` | cualquiera autenticado | Lista, filtro `course_id` |
| Horarios | `POST /api/v1/schedules` | admin | Alta |
| Horarios | `DELETE /api/v1/schedules/{id}` | admin | Baja |
| Matriculas | `GET /api/v1/enrollments` | cualquiera autenticado | Lista, filtros `student_id`/`course_id` |
| Matriculas | `POST /api/v1/enrollments` | cualquiera autenticado | Matricula a un estudiante en un curso |
| Matriculas | `PUT /api/v1/enrollments/{id}` | admin, teacher | Cambia estado (`active/completed/dropped`) |
| Matriculas | `DELETE /api/v1/enrollments/{id}` | admin, teacher | Elimina matricula |
| Notas | `GET /api/v1/grades` | cualquiera autenticado | Lista, filtro `enrollment_id` |
| Notas | `POST /api/v1/grades` | admin, teacher | Registra nota (dispara notificacion websocket) |
| Notas | `PUT /api/v1/grades/{id}` | admin, teacher | Actualiza nota |
| Notas | `DELETE /api/v1/grades/{id}` | admin, teacher | Elimina nota |
| Websocket | `WS /ws/notifications?token=<jwt>` | cualquiera autenticado | Notificaciones en tiempo real (p.ej. `new_grade`) |
| Salud | `GET /health` | publico | Liveness check |

## Codigos de error

Todas las respuestas de error siguen el formato `{"detail": "mensaje"}` y
usan codigos HTTP semanticos (ver `app/exceptions.py`):

| Codigo | Significado en esta API |
|---|---|
| 401 | Token ausente/invalido o credenciales incorrectas |
| 403 | Usuario autenticado pero sin permisos para la accion (rol incorrecto) |
| 404 | Recurso no encontrado |
| 409 | Conflicto (email duplicado, matricula duplicada) |
| 422 | Error de validacion de payload (tipos, rangos, campos requeridos) |
| 500 | Error inesperado del servidor (se registra en logs) |

## Ejemplo rapido con curl

```bash
# 1. Registro
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@academiaf5.dev", "password": "clave12345", "role": "admin"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@academiaf5.dev&password=clave12345" | jq -r .access_token)

# 3. Crear un curso
curl -X POST http://localhost:8000/api/v1/courses \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name": "Introduccion a Python", "credits": 4}'
```
