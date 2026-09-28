# Gestion del equipo y del proceso

## Contexto

Este proyecto se ha desarrollado en el marco de un bootcamp, con una
persona como responsable tecnica unica del producto. Para practicar de
forma realista la competencia de **gestion de equipos tecnicos**, el
proyecto se ha organizado *como si* lo ejecutara un equipo pequeno,
asumiendo explicitamente los distintos roles Scrum en vez de trabajar sin
estructura. Esto deja evidencia de: definicion de objetivos, reparto de
responsabilidades, ceremonias y comunicacion, que es lo que un tribunal
o un equipo real evaluarian en un proyecto colaborativo.

## Roles asumidos

| Rol | Responsabilidad en este proyecto |
|---|---|
| **Product Owner** | Prioriza el backlog ([kanban.md](kanban.md)), decide que entra en cada sprint y acepta las historias completadas frente a los criterios de aceptacion. |
| **Scrum Master** | Vela por el timebox (2 sprints de 1 semana), elimina bloqueos (p. ej. decidir pragmaticamente fijar `bcrypt==4.0.1` en vez de perder mas tiempo investigando alternativas) y facilita la retrospectiva. |
| **Desarrollo Backend** | Modelo de datos, API REST, autenticacion, tests. |
| **Desarrollo Frontend** | SPA en React, consumo de la API, experiencia de usuario. |
| **Asistente de IA (pair programmer)** | Se ha usado Claude Code como companero de programacion para acelerar el scaffolding (modelos, routers, tests), sugerir correcciones (p. ej. el bug de rutas `/students/{id}` vs `/students/export`) y generar documentacion base. Toda sugerencia se ha revisado, ejecutado localmente (tests, build) y validado antes de aceptarla — el criterio final es siempre humano. |

## Objetivos y comunicacion

- **Objetivo del proyecto** (definido antes de escribir codigo): digitalizar
  la gestion academica de un centro educativo con una API REST + base de
  datos relacional, reemplazando hojas de calculo manuales.
- **Definicion de "hecho"** para cada historia de usuario: endpoint
  implementado + tests en verde + documentado en `docs/api.md` (ver
  [kanban.md](kanban.md) para el detalle historia por historia).
- **Canal de comunicacion de decisiones**: este mismo repositorio. Las
  decisiones de arquitectura quedan registradas como ADRs
  (`docs/adr/`), y el porque de cada compromiso tecnico queda en la
  retrospectiva (`docs/retrospective.md`) en lugar de perderse en un chat.
- **Ceremonias**:
  - *Planning* al inicio de cada sprint: seleccionar historias del
    backlog (ver tablas de `kanban.md`).
  - *Daily* (autoseguimiento diario del avance frente al sprint).
  - *Review*: verificar contra los criterios de aceptacion (ejecutar la
    suite de tests + probar el endpoint/pantalla manualmente).
  - *Retrospectiva* al cierre de cada sprint (`docs/retrospective.md`).

## Como escalaria esto a un equipo real

Si el equipo creciera, los limites de responsabilidad definidos arriba se
convertirian en *code owners* de carpetas (`backend/` vs `frontend/`),
las ADRs pasarian a requerir aprobacion de al menos otra persona, y el
tablero Kanban se moveria a una herramienta compartida (Trello/Jira) con
notificaciones automaticas al mover una tarjeta a "En revision".
