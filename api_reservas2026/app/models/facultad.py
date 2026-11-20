from pydantic import BaseModel
from typing import Optional

class Facultad(BaseModel):
    id_facultad: Optional[int] = None
    nombre_facultad: str
    edificio_principal: str
    descripcion: Optional[str] = None