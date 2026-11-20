from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CheckIn(BaseModel):
    id_check_in: Optional[int] = None
    id_reserva: int
    hora_ingreso_real: Optional[datetime] = None
    estado_asistencia: str = "Pendiente"
