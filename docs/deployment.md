# Despliegue en la nube: Neon + Render + Vercel

Guía paso a paso para desplegar Academia F5 en producción usando servicios
gratuitos: **Neon** (PostgreSQL), **Render** (API backend, vía Docker) y
**Vercel** (frontend React). Pensada para preparar una demo/presentación.

Orden recomendado: **Neon → Render → Vercel → volver a Render** (para
terminar de configurar CORS con la URL real del frontend).

## 0. Antes de empezar

- El código debe estar en `main` de tu repositorio de GitHub (Render y
  Vercel despliegan automáticamente en cada push a la rama configurada).
- Necesitas cuentas gratuitas en [neon.tech](https://neon.tech),
  [render.com](https://render.com) y [vercel.com](https://vercel.com)
  (puedes registrarte con tu cuenta de GitHub en las tres, es lo más
  rápido).

## 1. Neon — base de datos PostgreSQL

1. Entra en [console.neon.tech](https://console.neon.tech) y crea un
   **New Project** (elige la región más cercana, p. ej. Frankfurt/EU).
2. Neon crea automáticamente una base de datos (`neondb`) y te muestra un
   **Connection string** en el dashboard. Usa la variante **"Pooled
   connection"** (recomendada para apps web: usa PgBouncer y evita agotar
   el límite de conexiones simultáneas del plan gratuito). Tendrá esta
   pinta:

   ```
   postgres://neondb_owner:AbC123...@ep-cool-name-12345-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
   ```

3. **Cópiala tal cual** — no hace falta editarla. El backend ya normaliza
   automáticamente el esquema `postgres://` a `postgresql+psycopg2://`
   (ver `app/core/config.py`) y el `sslmode=require` que exige Neon viaja
   sin problemas como parte de la URL.
4. Guarda esa cadena, la necesitas en el paso 2.

## 2. Render — API backend (Docker)

### Opción A — Blueprint (recomendada, usa `render.yaml`)

1. En [dashboard.render.com](https://dashboard.render.com): **New** →
   **Blueprint**.
2. Conecta tu cuenta de GitHub y selecciona este repositorio (rama
   `main`). Render detecta el archivo `render.yaml` de la raíz.
3. Render te pedirá rellenar las variables marcadas `sync: false`:
   - `DATABASE_URL`: pega la connection string de Neon del paso 1.
   - `CORS_ORIGINS`: de momento pon `["http://localhost:5173"]` (lo
     actualizaremos en el paso 4 con la URL real de Vercel).
4. Pulsa **Apply**. Render construye la imagen Docker (`backend/Dockerfile`)
   y despliega. La primera build tarda 3-5 minutos.
5. Cuando termine, Render te da una URL pública, p. ej.
   `https://academia-f5-api.onrender.com`. Compruébala:

   ```bash
   curl https://academia-f5-api.onrender.com/health
   # {"status":"ok"}
   ```

   Y abre `https://academia-f5-api.onrender.com/docs` en el navegador
   para ver Swagger funcionando en producción.

### Opción B — Manual (sin Blueprint)

Si prefieres no usar `render.yaml`: **New** → **Web Service** → conecta el
repo → **Root Directory**: `backend` → **Runtime**: `Docker` → añade las
mismas variables de entorno a mano en la pestaña **Environment** (ver la
lista en `render.yaml` o en `backend/.env.example`) → **Create Web
Service**.

> ⚠️ El plan gratuito de Render "duerme" el servicio tras ~15 min sin
> trafico; la primera petición tras dormir tarda ~30-50s en responder
> (cold start). Antes de una presentación en vivo, abre la URL de
> `/health` unos minutos antes para "despertarlo".

## 3. Vercel — frontend (React + Vite)

1. En [vercel.com/new](https://vercel.com/new), importa el mismo
   repositorio de GitHub.
2. **Root Directory**: `frontend` (importante en un monorepo — Vercel
   pregunta esto al importar).
3. Vercel detecta automáticamente el framework (Vite). Deja los comandos
   por defecto (`npm run build`, output `dist`).
4. En **Environment Variables**, añade (con el mismo valor para
   *Production*, *Preview* y *Development* si quieres probar ramas):
   - `VITE_API_URL` = `https://academia-f5-api.onrender.com/api/v1`
   - `VITE_WS_URL` = `wss://academia-f5-api.onrender.com/ws/notifications`

   (usa la URL real que te dio Render en el paso 2; nota el esquema
   `wss://`, no `ws://`, porque el sitio se sirve por HTTPS).
5. **Deploy**. Vercel te da una URL pública, p. ej.
   `https://academia-f5.vercel.app`.

> Las variables `VITE_*` se incrustan en el bundle **en tiempo de build**
> (es como funciona Vite). Si las cambias despues, tienes que forzar un
> redeploy desde el dashboard de Vercel para que se apliquen.

## 4. Vuelta a Render — cerrar el CORS

Ahora que tienes la URL de Vercel, vuelve a Render → tu servicio
`academia-f5-api` → **Environment** → edita `CORS_ORIGINS`:

```
["https://academia-f5.vercel.app"]
```

Guarda: Render redespliega automáticamente (no hace falta hacer push,
solo cambia el env var). Espera a que el estado vuelva a "Live".

## 5. Probar el despliegue completo

1. Abre `https://academia-f5.vercel.app` — deberías ver la pantalla de
   login.
2. Regístrate como admin vía Swagger
   (`https://academia-f5-api.onrender.com/docs` → `POST /auth/register`
   con `"role": "admin"`) o crea el usuario y luego promuévelo
   directamente en Neon (tabla `users`, columna `role`).
3. Inicia sesión desde el frontend, crea un curso, matricula un
   estudiante y registra una nota — si el estudiante tiene el dashboard
   abierto en otra pestaña, la notificación debería llegar al instante
   (confirma que el WebSocket atraviesa Render + HTTPS correctamente).

## Notas para el día de la presentación

- **Cold starts**: visita `/health` (Render) unos 5 minutos antes de
  presentar para que el contenedor y la conexión a Neon ya estén
  "calientes" y no haya esperas incómodas en directo.
- **Datos de demo**: crea de antemano un admin, un par de profesores,
  cursos y estudiantes de ejemplo, para no tener que teclear altas en
  vivo.
- **Logs en vivo**: Render → tu servicio → pestaña **Logs** te deja ver
  las peticiones entrando en tiempo real, útil para depurar si algo falla
  durante la demo.
- **Rollback rápido**: si un deploy rompe algo justo antes de presentar,
  Render permite volver a un deploy anterior desde **Events** →
  "Rollback" en un clic.
