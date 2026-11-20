from fastapi import APIRouter, HTTPException
from app.models.espacio_recurso import EspacioRecurso
from app.repositories.espacio_recurso_repo import EspacioRecursoRepository

router = APIRouter(prefix="/espacios-recursos", tags=["Asignación de Recursos a Espacios"])
repo = EspacioRecursoRepository()

@router.get("/")
def listar_asignaciones():
    try:
        return repo.obtener_todas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/espacio/{espacio_id}")
def listar_recursos_de_espacio(espacio_id: int):
    try:
        return repo.obtener_por_espacio(espacio_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{espacio_recurso_id}")
def obtener_asignacion(espacio_recurso_id: int):
    try:
        asignacion = repo.obtener_por_id(espacio_recurso_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        return asignacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_asignacion(espacio_recurso: EspacioRecurso):
    try:
        nuevo_id = repo.crear(espacio_recurso)
        return {"mensaje": "Asignación creada exitosamente", "id_espacio_recurso": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{espacio_recurso_id}")
def actualizar_asignacion(espacio_recurso_id: int, espacio_recurso: EspacioRecurso):
    try:
        exito = repo.actualizar(espacio_recurso_id, espacio_recurso)
        if not exito:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        return {"mensaje": "Asignación actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{espacio_recurso_id}")
def eliminar_asignacion(espacio_recurso_id: int):
    try:
        exito = repo.eliminar(espacio_recurso_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        return {"mensaje": "Asignación eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))