from fastapi import APIRouter, HTTPException
from app.models.auditoria import Auditoria
from app.repositories.auditoria_repo import AuditoriaRepository

router = APIRouter(prefix="/auditoria", tags=["Auditoría del Sistema"])
repo = AuditoriaRepository()

@router.get("/")
def listar_auditoria():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tabla/{tabla_afectada}")
def listar_auditoria_por_tabla(tabla_afectada: str):
    try:
        return repo.obtener_por_tabla(tabla_afectada)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{auditoria_id}")
def obtener_registro_auditoria(auditoria_id: int):
    try:
        registro = repo.obtener_por_id(auditoria_id)
        if not registro:
            raise HTTPException(status_code=404, detail="Registro de auditoría no encontrado")
        return registro
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def crear_registro_auditoria(auditoria: Auditoria):
    try:
        nuevo_id = repo.crear(auditoria)
        return {"mensaje": "Registro de auditoría creado exitosamente", "id_auditoria": nuevo_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))