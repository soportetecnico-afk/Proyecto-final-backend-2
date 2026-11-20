// URL base del backend. En Render se configura mediante VITE_API_BASE_URL.
// En desarrollo, si no existe la variable, utiliza FastAPI local.
export const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
