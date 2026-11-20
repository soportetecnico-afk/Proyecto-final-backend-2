from pydantic import BaseModel
from typing import Optional

class Notificacion(BaseModel):
    id_notificacion: Optional[int] = None
    id_usuario: int
    id_reserva: Optional[int] = None
    tipo_canal: str
    mensaje_texto: str
    enviada: bool = False
