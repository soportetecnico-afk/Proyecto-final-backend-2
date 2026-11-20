from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    rutas_reservas, rutas_usuarios, rutas_espacios, rutas_facultades, rutas_roles,
    rutas_tipos_espacio, rutas_tipos_evento, rutas_recursos, rutas_espacios_recursos,
    rutas_bloqueos, rutas_check_ins, rutas_notificaciones, rutas_auditoria,
    rutas_modulos, rutas_modulosxrol, 
    rutas_reubicaciones, rutas_retroalimentaciones, rutas_reportes
)

app = FastAPI(
    title="API Reservas Universidad",
    description="Backend modular para gestión de espacios físicos",
    version="1.0.0"
)

# Configuración obligatoria de CORS para permitir la conexión con SvelteKit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectamos los módulos de rutas a la aplicación principal
app.include_router(rutas_reservas.router)
app.include_router(rutas_usuarios.router)
app.include_router(rutas_espacios.router)
app.include_router(rutas_facultades.router)
app.include_router(rutas_roles.router)
app.include_router(rutas_tipos_espacio.router)
app.include_router(rutas_tipos_evento.router)
app.include_router(rutas_recursos.router)
app.include_router(rutas_espacios_recursos.router)
app.include_router(rutas_bloqueos.router)
app.include_router(rutas_check_ins.router)
app.include_router(rutas_notificaciones.router)
app.include_router(rutas_auditoria.router)
app.include_router(rutas_modulos.router)
app.include_router(rutas_modulosxrol.router)
app.include_router(rutas_reubicaciones.router)
app.include_router(rutas_retroalimentaciones.router)
app.include_router(rutas_reportes.router)

@app.get("/")
def estado_api():
    return {"mensaje": "La API de Reservas se encuentra en línea y funcional"}