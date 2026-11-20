from fastapi import APIRouter, HTTPException
from app.models.reubicacion_reserva import ReubicacionReserva, ReubicacionReservaCrear, ReubicacionReservaActualizar
from app.repositories.reubicacion_reserva_repo import ReubicacionReservaRepository

router = APIRouter(prefix="/reubicaciones", tags=["Reubicaciones de Emergencia"])
repo = ReubicacionReservaRepository()

@router.get("/")
def listar_reubicaciones():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{reubicacion_id}")
def obtener_reubicacion(reubicacion_id: int):
    try:
        registro = repo.obtener_por_id(reubicacion_id)
        if not registro:
            raise HTTPException(status_code=404, detail="Reubicación no encontrada")
        return registro
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_reubicacion(reubicacion: ReubicacionReservaCrear):
    try:
        nuevo_id = repo.crear(reubicacion)
        return {"mensaje": "Reubicación creada exitosamente", "id_reubicacion": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{reubicacion_id}")
def actualizar_reubicacion(reubicacion_id: int, reubicacion: ReubicacionReservaActualizar):
    try:
        actualizado = repo.actualizar(reubicacion_id, reubicacion)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Reubicación no encontrada o no se pudo actualizar")
        return {"mensaje": "Reubicación actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{reubicacion_id}")
def eliminar_reubicacion(reubicacion_id: int):
    try:
        eliminado = repo.eliminar(reubicacion_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Reubicación no encontrada")
        return {"mensaje": "Reubicación eliminada lógicamente (estado=false)"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))