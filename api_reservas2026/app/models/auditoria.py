from pydantic import BaseModel
from typing import Optional

class Auditoria(BaseModel):
    id_auditoria: Optional[int] = None
    id_usuario: Optional[int] = None
    tabla_afectada: str
    id_registro: Optional[int] = None
    accion: str
    descripcion: Optional[str] = None
