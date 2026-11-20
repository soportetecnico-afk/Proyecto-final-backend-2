from pydantic import BaseModel
from typing import Optional

class TipoEspacio(BaseModel):
    id_tipo_espacio: Optional[int] = None
    nombre_tipo: str
    requiere_aprobacion: bool = False
    color_calendario: Optional[str] = None
