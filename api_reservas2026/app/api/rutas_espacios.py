from fastapi import APIRouter, HTTPException
from app.models.espacio import Espacio
from app.repositories.espacio_repo import EspacioRepository

router = APIRouter(prefix="/espacios", tags=["Gestión de Espacios"])
repo = EspacioRepository()

@router.get("/")
def listar_espacios():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{espacio_id}")
def obtener_espacio(espacio_id: int):
    try:
        espacio = repo.obtener_por_id(espacio_id)
        if not espacio:
            raise HTTPException(status_code=404, detail="Espacio no encontrado")
        return espacio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_espacio(espacio: Espacio):
    try:
        nuevo_id = repo.crear(espacio)
        return {"mensaje": "Espacio creado exitosamente", "id_espacio": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{espacio_id}")
def actualizar_espacio(espacio_id: int, espacio: Espacio):
    try:
        exito = repo.actualizar(espacio_id, espacio)
        if not exito:
            raise HTTPException(status_code=404, detail="Espacio no encontrado")
        return {"mensaje": "Espacio actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{espacio_id}")
def eliminar_espacio(espacio_id: int):
    try:
        exito = repo.eliminar(espacio_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Espacio no encontrado")
        return {"mensaje": "Espacio eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))