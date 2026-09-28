# ADR 0001 — Arquitectura en capas con patron Repository

**Estado:** Aceptada

## Contexto

Necesitamos una estructura de codigo que permita anadir recursos nuevos
(estudiantes, cursos, matriculas, notas...) de forma consistente, testear
la logica de negocio sin depender de HTTP ni de una base de datos real, y
mantener el acceso a datos centralizado para poder optimizarlo (cache,
consultas complejas) sin tocar la capa HTTP.

## Decision

Organizamos `backend/app/` en cuatro capas con una direccion de
dependencia unica (de arriba hacia abajo):

```
routers/      → capa HTTP: parsing de request, codigos de estado, auth por endpoint
services/     → logica de negocio y orquestacion (valida reglas, dispara notificaciones)
repositories/ → acceso a datos (patron Repository sobre SQLAlchemy)
models/       → entidades ORM (SQLAlchemy) + schemas/ (DTOs Pydantic)
```

- `routers/` nunca usa `db.query(...)` directamente: siempre pasa por un
  `Service`.
- `services/` nunca construye SQL/ORM a mano: usa un `Repository`
  (`BaseRepository[Model]` con `get/list/create/update/delete` genericos,
  mas metodos especificos cuando hace falta, p. ej.
  `EnrollmentRepository.get_by_student_and_course`).
- Las excepciones de dominio (`NotFoundError`, `ConflictError`, etc.) se
  lanzan en `services/` y se traducen a codigos HTTP en un unico sitio
  (`app/exceptions.py` + `app/main.py`), en vez de repartir
  `HTTPException` por todos los routers.

## Alternativas consideradas

- **Todo en el router** (lo mas rapido de escribir al principio): se
  descarto porque mezclar parsing HTTP, reglas de negocio y SQL en la
  misma funcion hace los tests de integracion la unica forma de probar
  nada, y cualquier cambio de framework (p. ej. quitar FastAPI) obligaria
  a reescribir la logica de negocio.
- **ORM Active Record** (metodos `save()`/`delete()` en el propio modelo):
  descartado porque SQLAlchemy 2.0 favorece el patron Data Mapper (sesion
  explicita) y mezclar reglas de negocio en el modelo dificulta testear
  esas reglas sin una base de datos.

## Consecuencias

- Los tests unitarios de `services/` (ver `tests/unit/test_course_service.py`)
  se ejecutan contra una sesion SQLAlchemy real (SQLite), sin pasar por
  HTTP, lo que los hace rapidos y focalizados en la regla de negocio.
- Anadir un recurso nuevo implica tocar 4 archivos pequenos y previsibles
  (model, schema, repository, service, router) en vez de un archivo
  monolitico.
- Coste: mas archivos y algo de "boilerplate" para operaciones CRUD
  simples; se acepta porque el proyecto tiene 7 entidades y va a crecer.
