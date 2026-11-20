from fastapi import APIRouter, HTTPException
from app.models.modulo import Modulo
from app.repositories.modulo_repo import ModuloRepository

router = APIRouter(prefix="/modulos", tags=["Gestión de Módulos"])
repo = ModuloRepository()

@router.get("/")
def listar_modulos():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{modulo_id}")
def obtener_modulo(modulo_id: int):
    try:
        modulo = repo.obtener_por_id(modulo_id)
        if not modulo:
            raise HTTPException(status_code=404, detail="Módulo no encontrado")
        return modulo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_modulo(modulo: Modulo):
    try:
        nuevo_id = repo.crear(modulo)
        return {"mensaje": "Módulo creado exitosamente", "id_modulo": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{modulo_id}")
def actualizar_modulo(modulo_id: int, modulo: Modulo):
    try:
        exito = repo.actualizar(modulo_id, modulo)
        if not exito:
            raise HTTPException(status_code=404, detail="Módulo no encontrado")
        return {"mensaje": "Módulo actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{modulo_id}")
def eliminar_modulo(modulo_id: int):
    try:
        exito = repo.eliminar(modulo_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Módulo no encontrado")
        return {"mensaje": "Módulo eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))