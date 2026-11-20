from fastapi import APIRouter, HTTPException
from app.models.tipo_evento import TipoEvento
from app.repositories.tipo_evento_repo import TipoEventoRepository

router = APIRouter(prefix="/tipos-evento", tags=["Gestión de Tipos de Evento"])
repo = TipoEventoRepository()

@router.get("/")
def listar_tipos_evento():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tipo_evento_id}")
def obtener_tipo_evento(tipo_evento_id: int):
    try:
        tipo_evento = repo.obtener_por_id(tipo_evento_id)
        if not tipo_evento:
            raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")
        return tipo_evento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_tipo_evento(tipo_evento: TipoEvento):
    try:
        nuevo_id = repo.crear(tipo_evento)
        return {"mensaje": "Tipo de evento creado exitosamente", "id_tipo_evento": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tipo_evento_id}")
def actualizar_tipo_evento(tipo_evento_id: int, tipo_evento: TipoEvento):
    try:
        exito = repo.actualizar(tipo_evento_id, tipo_evento)
        if not exito:
            raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")
        return {"mensaje": "Tipo de evento actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tipo_evento_id}")
def eliminar_tipo_evento(tipo_evento_id: int):
    try:
        exito = repo.eliminar(tipo_evento_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")
        return {"mensaje": "Tipo de evento eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))