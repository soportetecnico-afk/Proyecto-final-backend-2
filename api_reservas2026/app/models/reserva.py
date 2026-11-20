from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class Reserva(BaseModel):
    id_reserva: Optional[int] = None
    id_usuario: int
    id_espacio: int
    id_tipo_evento: int
    id_aprobador: Optional[int] = None
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    cantidad_asistentes: int
    estado_reserva: str = "Pendiente"
    fecha_limite_aprobacion: Optional[datetime] = None
