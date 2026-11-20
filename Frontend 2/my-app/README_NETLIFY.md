# Despliegue del frontend CUL en Netlify

## Arquitectura

- Frontend: SvelteKit 2 + Svelte 5, publicado en Netlify.
- Backend: FastAPI, publicado en Render.
- Base de datos: PostgreSQL en Neon. Las credenciales de Neon permanecen exclusivamente en el backend.

## Configuración de Netlify

Repositorio: `soportetecnico-afk/Proyecto-final-backend-2`

- Base directory: `Frontend 2/my-app`
- Build command: `npm run build`
- Publish directory: `build`
- Node: 22 (el proyecto declara `>=22.12.0 <23`).

Netlify instalará las dependencias npm antes de ejecutar el build.

## Variable de entorno obligatoria

En Site configuration > Environment variables, crear:

- Key: `VITE_API_BASE_URL`
- Value: `https://proyecto-final-backend-2-z236.onrender.com`

La variable se incorpora durante la compilación; al cambiarla hay que volver a desplegar. Las variables `VITE_*` son visibles desde el navegador: nunca guardar contraseñas ni secretos allí.

## CORS del backend

Después de crear el sitio, copiar su dominio HTTPS real de Netlify y agregarlo a `allow_origins` del middleware CORS de FastAPI en Render. No usar `*` como sustituto de una lista de orígenes autorizados. El backend no venía incluido en este ZIP, así que este cambio debe hacerse en el repositorio/backend correspondiente.

API: `https://proyecto-final-backend-2-z236.onrender.com`
Documentación: `https://proyecto-final-backend-2-z236.onrender.com/docs`

## Desarrollo local

Crear `.env` a partir de `.env.example` y mantener `VITE_API_BASE_URL=http://127.0.0.1:8000` cuando FastAPI se ejecute localmente.
