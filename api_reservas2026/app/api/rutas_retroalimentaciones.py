from fastapi import APIRouter, HTTPException
from app.models.retroalimentacion_reserva import RetroalimentacionReserva, RetroalimentacionReservaCrear, RetroalimentacionReservaActualizar
from app.repositories.retroalimentacion_reserva_repo import RetroalimentacionReservaRepository

router = APIRouter(prefix="/retroalimentaciones", tags=["Retroalimentación Post-Reserva"])
repo = RetroalimentacionReservaRepository()

@router.get("/")
def listar_retroalimentaciones():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{retroalimentacion_id}")
def obtener_retroalimentacion(retroalimentacion_id: int):
    try:
        registro = repo.obtener_por_id(retroalimentacion_id)
        if not registro:
            raise HTTPException(status_code=404, detail="Retroalimentación no encontrada")
        return registro
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_retroalimentacion(retroalimentacion: RetroalimentacionReservaCrear):
    try:
        if retroalimentacion.calificacion_espacio < 1 or retroalimentacion.calificacion_espacio > 5:
             raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5")
        nuevo_id = repo.crear(retroalimentacion)
        return {"mensaje": "Retroalimentación creada exitosamente", "id_retroalimentacion": nuevo_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{retroalimentacion_id}")
def actualizar_retroalimentacion(retroalimentacion_id: int, retroalimentacion: RetroalimentacionReservaActualizar):
    try:
        if retroalimentacion.calificacion_espacio and (retroalimentacion.calificacion_espacio < 1 or retroalimentacion.calificacion_espacio > 5):
             raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5")
        
        actualizado = repo.actualizar(retroalimentacion_id, retroalimentacion)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Retroalimentación no encontrada")
        return {"mensaje": "Retroalimentación actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{retroalimentacion_id}")
def eliminar_retroalimentacion(retroalimentacion_id: int):
    try:
        eliminado = repo.eliminar(retroalimentacion_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Retroalimentación no encontrada")
        return {"mensaje": "Retroalimentación eliminada lógicamente (estado=false)"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))