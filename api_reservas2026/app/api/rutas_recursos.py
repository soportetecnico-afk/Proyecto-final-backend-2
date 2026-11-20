from fastapi import APIRouter, HTTPException
from app.models.recurso import Recurso
from app.repositories.recurso_repo import RecursoRepository

router = APIRouter(prefix="/recursos", tags=["Gestión de Recursos"])
repo = RecursoRepository()

@router.get("/")
def listar_recursos():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{recurso_id}")
def obtener_recurso(recurso_id: int):
    try:
        recurso = repo.obtener_por_id(recurso_id)
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return recurso
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_recurso(recurso: Recurso):
    try:
        nuevo_id = repo.crear(recurso)
        return {"mensaje": "Recurso creado exitosamente", "id_recurso": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{recurso_id}")
def actualizar_recurso(recurso_id: int, recurso: Recurso):
    try:
        exito = repo.actualizar(recurso_id, recurso)
        if not exito:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return {"mensaje": "Recurso actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{recurso_id}")
def eliminar_recurso(recurso_id: int):
    try:
        exito = repo.eliminar(recurso_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return {"mensaje": "Recurso eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))