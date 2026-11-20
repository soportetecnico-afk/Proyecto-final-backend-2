from fastapi import APIRouter, HTTPException
from app.models.bloqueo_mantenimiento import BloqueoMantenimiento
from app.repositories.bloqueo_mantenimiento_repo import BloqueoMantenimientoRepository

router = APIRouter(prefix="/bloqueos", tags=["Gestión de Bloqueos y Mantenimiento"])
repo = BloqueoMantenimientoRepository()

@router.get("/")
def listar_bloqueos():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{bloqueo_id}")
def obtener_bloqueo(bloqueo_id: int):
    try:
        bloqueo = repo.obtener_por_id(bloqueo_id)
        if not bloqueo:
            raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
        return bloqueo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_bloqueo(bloqueo: BloqueoMantenimiento):
    try:
        nuevo_id = repo.crear(bloqueo)
        return {"mensaje": "Bloqueo creado exitosamente", "id_bloqueo": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{bloqueo_id}")
def actualizar_bloqueo(bloqueo_id: int, bloqueo: BloqueoMantenimiento):
    try:
        exito = repo.actualizar(bloqueo_id, bloqueo)
        if not exito:
            raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
        return {"mensaje": "Bloqueo actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{bloqueo_id}")
def eliminar_bloqueo(bloqueo_id: int):
    try:
        exito = repo.eliminar(bloqueo_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
        return {"mensaje": "Bloqueo eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))