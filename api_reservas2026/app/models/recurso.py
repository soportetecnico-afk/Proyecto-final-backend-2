from pydantic import BaseModel
from typing import Optional

class Recurso(BaseModel):
    id_recurso: Optional[int] = None
    nombre_recurso: str
    categoria: str
    estado_mantenimiento: str = "Optimo"
