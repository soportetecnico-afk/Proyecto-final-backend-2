from fastapi import APIRouter, HTTPException
from app.models.facultad import Facultad
from app.repositories.facultad_repo import FacultadRepository

router = APIRouter(prefix="/facultades", tags=["Gestión de Facultades"])
repo = FacultadRepository()

@router.get("/")
def listar_facultades():
    try:
        return repo.obtener_todas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{facultad_id}")
def obtener_facultad(facultad_id: int):
    try:
        facultad = repo.obtener_por_id(facultad_id)
        if not facultad:
            raise HTTPException(status_code=404, detail="Facultad no encontrada")
        return facultad
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_facultad(facultad: Facultad):
    try:
        nuevo_id = repo.crear(facultad)
        return {"mensaje": "Facultad creada exitosamente", "id_facultad": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{facultad_id}")
def actualizar_facultad(facultad_id: int, facultad: Facultad):
    try:
        exito = repo.actualizar(facultad_id, facultad)
        if not exito:
            raise HTTPException(status_code=404, detail="Facultad no encontrada")
        return {"mensaje": "Facultad actualizada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{facultad_id}")
def eliminar_facultad(facultad_id: int):
    try:
        exito = repo.eliminar(facultad_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Facultad no encontrada")
        return {"mensaje": "Facultad eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))