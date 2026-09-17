# Retrospectiva del proyecto — Academia F5

**Duracion:** 2 semanas (2 sprints de 1 semana). **Formato:** Start / Stop / Continue.

## Sprint 1 — Fundacion

### 😀 Que funciono bien (Continue)
- Definir el modelo de datos (7 tablas, relaciones 1:1/1:N/N:M) antes de
  escribir un solo endpoint evito retrabajo: el resto del backend
  (repositorios, servicios, schemas) se construyo directamente sobre ese
  esquema sin cambios de ruptura.
- Separar la logica en capas (`routers` → `services` → `repositories` →
  `models`) hizo que anadir endpoints nuevos (p. ej. `/students/export`)
  fuese mecanico y facil de testear de forma aislada.
- Escribir los tests a la vez que cada endpoint (no al final) detecto
  pronto varios bugs reales: una incompatibilidad de `passlib`/`bcrypt`
  con las versiones mas recientes, y un error de FastAPI al anotar
  `-> Page[Course]` que rompia el arranque de la app.

### 😕 Que no funciono tan bien (Stop)
- No fijar versiones exactas de dependencias transitivas (`bcrypt`) causo
  una tarde perdida depurando un error criptico de "password cannot be
  longer than 72 bytes" que en realidad era un problema de compatibilidad
  entre `passlib==1.7.4` y `bcrypt>=4.1`.
- Usar dominios de prueba `.test` en los tests de integracion fallaba por
  validacion de `email-validator` (dominio reservado por RFC 2606); tuvo
  que corregirse en todos los fixtures.

### 🎯 Acciones para el sprint 2 (Start)
- Fijar `bcrypt==4.0.1` explicitamente en `requirements.txt` en vez de
  dejar que `pip` resuelva la ultima version compatible con `passlib`.
- Documentar en el README el dominio de email seguro para pruebas
  (`@academiaf5.dev`) para que no se repita el problema en tests futuros.

## Sprint 2 — Funcionalidad avanzada

### 😀 Que funciono bien (Continue)
- Anadir cache en memoria (`TTLCache`) con invalidacion explicita en cada
  mutacion fue mas simple y suficiente para el alcance del proyecto que
  levantar Redis, y quedo aislado en un unico modulo (`app/core/cache.py`)
  facil de sustituir el dia que haga falta escalar a varias instancias.
- El canal de WebSocket de notificaciones reutiliza el mismo JWT que la
  API REST (no hubo que inventar un segundo mecanismo de autenticacion).
- Generar la migracion inicial con Alembic `--autogenerate` y validarla
  con un ciclo `upgrade`/`downgrade` en un SQLite temporal dio confianza
  antes de tocar una base de datos real.

### 😕 Que no funciono tan bien (Stop)
- El frontend inicial no exponia el `student_id` del usuario logueado
  (el endpoint de estudiantes es solo para staff), lo que bloqueaba el
  autoservicio de matricula. Hubo que anadir `GET /students/me` a
  mitad de sprint en lugar de haberlo previsto en el diseno de la API.
- El orden de las rutas en FastAPI importa: `/students/export` y
  `/students/me` deben declararse antes de `/students/{student_id}` o el
  path param `int` intenta convertir literales como "export"/"me" y
  devuelve 422 en vez de resolver la ruta correcta. Nos llevo tiempo
  diagnosticarlo la primera vez.

### 🎯 Acciones para futuras iteraciones
- Al diseñar un recurso REST, decidir desde el principio que acciones
  necesita "el propio usuario sobre si mismo" (`/me`) ademas de las
  acciones de staff, para no anadirlas a posteriori.
- Anadir un test de "smoke" que golpee cada ruta declarada en la app y
  falle si el orden de registro produce colisiones de path.

## Metricas del proyecto

- **Cobertura de tests (backend):** 91% (`pytest --cov=app`).
- **Endpoints REST:** 27, mas 1 canal WebSocket.
- **Tablas de base de datos:** 7, con migraciones versionadas en Alembic.
- **Historias de usuario completadas:** 14 de 17 (3 quedan en backlog para
  una tercera iteracion, ver [kanban.md](kanban.md)).
