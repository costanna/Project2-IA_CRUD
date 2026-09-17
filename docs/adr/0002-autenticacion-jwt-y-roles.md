# ADR 0002 — Autenticacion con JWT y autorizacion por roles

**Estado:** Aceptada

## Contexto

La API tiene tres tipos de usuario con permisos muy distintos
(`admin`, `teacher`, `student`) y debe exponer un canal WebSocket ademas
de REST. Necesitamos un mecanismo de autenticacion sin estado (la API no
debe depender de sesiones en memoria/sticky sessions para poder escalar
horizontalmente) que funcione igual en ambos canales.

## Decision

- **JWT firmado con `SECRET_KEY`** (HS256), emitido en `POST /auth/login`
  usando el flujo estandar `OAuth2PasswordBearer` de FastAPI. El token
  incluye `sub` (email) y `role` como claims.
- **RBAC declarativo** con una factoria de dependencias,
  `require_roles(*roles)` (`app/deps.py`), que se anade como
  `dependencies=[Depends(require_roles(UserRole.ADMIN))]` en cada ruta.
  Esto hace visible de un vistazo, en la firma del endpoint, quien puede
  llamarlo, en vez de esconder un `if current_user.role != "admin"` dentro
  del cuerpo de la funcion.
- El **mismo JWT se reutiliza en el WebSocket** (`/ws/notifications?token=...`)
  decodificandolo manualmente (los WebSockets no soportan cabeceras
  `Authorization` de forma nativa en el navegador), evitando inventar un
  segundo mecanismo de autenticacion solo para ese canal.

## Alternativas consideradas

- **Sesiones de servidor (cookies + almacenamiento en servidor)**:
  descartado por anadir estado al servidor (dificulta escalar a varias
  instancias) sin aportar beneficios de seguridad relevantes para este
  proyecto.
- **Permisos verificados a mano en cada funcion de servicio**: descartado
  porque duplicaria la logica de autorizacion en cada metodo y seria mas
  facil olvidar comprobarla en un endpoint nuevo.

## Consecuencias

- Revocar un token antes de que expire no es posible sin una lista negra
  adicional (aceptable para el alcance del proyecto: expiracion corta,
  60 minutos por defecto, configurable por `.env`).
- Anadir un cuarto rol en el futuro es tan simple como anadir un valor al
  enum `UserRole` y decidir en que `require_roles(...)` deberia aparecer.
