# Despliegue del Frontend CUL en Render

## Configuración del servicio Web Service

- Runtime: Node
- Build Command: `npm install && npm run build`
- Start Command: `npm start`
- Variable de entorno:
  - Key: `VITE_API_BASE_URL`
  - Value: `https://proyecto-final-backend-2-z236.onrender.com`

La variable `VITE_API_BASE_URL` se incorpora durante la compilación. Si se cambia la URL del backend, se debe actualizar la variable y volver a desplegar el frontend.

## Desarrollo local

Crea un archivo `.env` a partir de `.env.example` y deja `VITE_API_BASE_URL=http://127.0.0.1:8000` si FastAPI se ejecuta localmente.

## Importante

No se debe colocar la contraseña de Neon ni ninguna credencial de la base de datos en el frontend. El navegador solo debe comunicarse con la API pública de FastAPI; las credenciales de PostgreSQL permanecen exclusivamente en las variables de entorno del backend.
