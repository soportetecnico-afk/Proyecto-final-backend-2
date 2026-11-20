from pydantic import BaseModel
from typing import Optional

class Espacio(BaseModel):
    id_espacio: Optional[int] = None
    nombre_espacio: str
    capacidad_aforo: int
    ubicacion_piso: str
    id_tipo_espacio: int
    id_facultad: Optional[int] = None
    permite_sabado: bool = False