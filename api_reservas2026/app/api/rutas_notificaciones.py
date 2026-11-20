from fastapi import APIRouter, HTTPException
from app.models.notificacion import Notificacion
from app.repositories.notificacion_repo import NotificacionRepository

router = APIRouter(prefix="/notificaciones", tags=["Gestión de Notificaciones"])
repo = NotificacionRepository()

@router.get("/")
def listar_notificaciones():
    try:
        return repo.obtener_todas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usuario/{usuario_id}")
def listar_notificaciones_de_usuario(usuario_id: int):
    try:
        return repo.obtener_por_usuario(usuario_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notificacion_id}")
def obtener_notificacion(notificacion_id: int):
    try:
        notificacion = repo.obtener_por_id(notificacion_id)
        if not notificacion:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        return notificacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_notificacion(notificacion: Notificacion):
    try:
        nuevo_id = repo.crear(notificacion)
        return {"mensaje": "Notificación creada exitosamente", "id_notificacion": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{notificacion_id}")
def actualizar_notificacion(notificacion_id: int, notificacion: Notificacion):
    try:
        exito = repo.actualizar(notificacion_id, notificacion)
        if not exito:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        return {"mensaje": "Notificación actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{notificacion_id}")
def eliminar_notificacion(notificacion_id: int):
    try:
        exito = repo.eliminar(notificacion_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        return {"mensaje": "Notificación eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))