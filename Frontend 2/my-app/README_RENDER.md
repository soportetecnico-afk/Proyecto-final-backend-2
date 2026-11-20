# Arquitectura de despliegue del proyecto CUL

El frontend de este proyecto se publica en **Netlify**. El backend FastAPI permanece publicado en **Render** y se conecta con PostgreSQL en Neon.

Para desplegar el frontend, consulta `README_NETLIFY.md`.

La variable `VITE_API_BASE_URL` debe apuntar a la URL pública de FastAPI. Las credenciales de Neon y cualquier secreto del backend deben permanecer únicamente en el backend de Render; nunca deben incluirse en el frontend.
