from pydantic import BaseModel
from typing import Optional

class TipoEvento(BaseModel):
    id_tipo_evento: Optional[int] = None
    nombre_evento: str
    permite_sabado: bool = False
    requiere_aprobacion_especial: bool = False
