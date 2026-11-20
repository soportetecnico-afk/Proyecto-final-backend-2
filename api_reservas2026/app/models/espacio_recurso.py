from pydantic import BaseModel
from typing import Optional

class EspacioRecurso(BaseModel):
    id_espacio_recurso: Optional[int] = None
    id_espacio: int
    id_recurso: int
    cantidad_asignada: int = 1
