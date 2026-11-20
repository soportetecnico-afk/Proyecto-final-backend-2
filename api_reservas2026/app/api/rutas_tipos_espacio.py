from fastapi import APIRouter, HTTPException
from app.models.tipo_espacio import TipoEspacio
from app.repositories.tipo_espacio_repo import TipoEspacioRepository

router = APIRouter(prefix="/tipos-espacio", tags=["Gestión de Tipos de Espacio"])
repo = TipoEspacioRepository()

@router.get("/")
def listar_tipos_espacio():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tipo_espacio_id}")
def obtener_tipo_espacio(tipo_espacio_id: int):
    try:
        tipo_espacio = repo.obtener_por_id(tipo_espacio_id)
        if not tipo_espacio:
            raise HTTPException(status_code=404, detail="Tipo de espacio no encontrado")
        return tipo_espacio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_tipo_espacio(tipo_espacio: TipoEspacio):
    try:
        nuevo_id = repo.crear(tipo_espacio)
        return {"mensaje": "Tipo de espacio creado exitosamente", "id_tipo_espacio": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tipo_espacio_id}")
def actualizar_tipo_espacio(tipo_espacio_id: int, tipo_espacio: TipoEspacio):
    try:
        exito = repo.actualizar(tipo_espacio_id, tipo_espacio)
        if not exito:
            raise HTTPException(status_code=404, detail="Tipo de espacio no encontrado")
        return {"mensaje": "Tipo de espacio actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tipo_espacio_id}")
def eliminar_tipo_espacio(tipo_espacio_id: int):
    try:
        exito = repo.eliminar(tipo_espacio_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Tipo de espacio no encontrado")
        return {"mensaje": "Tipo de espacio eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))