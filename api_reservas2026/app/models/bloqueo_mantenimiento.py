from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BloqueoMantenimiento(BaseModel):
    id_bloqueo: Optional[int] = None
    id_espacio: int
    id_usuario_reporta: int
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo_bloqueo: str
    descripcion: Optional[str] = None
