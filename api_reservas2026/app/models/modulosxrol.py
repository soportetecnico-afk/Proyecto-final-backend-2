from pydantic import BaseModel
from typing import Optional

class ModulosXRol(BaseModel):
    id_modulosxrol: Optional[int] = None
    id_rol: int
    id_modulo: int
