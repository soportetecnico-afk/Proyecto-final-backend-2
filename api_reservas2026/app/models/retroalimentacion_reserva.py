from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RetroalimentacionReservaBase(BaseModel):
    id_reserva: int
    id_usuario_reporta: int
    calificacion_espacio: int
    comentario_novedad: Optional[str] = None
    reporta_dano: Optional[bool] = False
    estado: Optional[bool] = True

class RetroalimentacionReservaCrear(RetroalimentacionReservaBase):
    pass

class RetroalimentacionReservaActualizar(BaseModel):
    calificacion_espacio: Optional[int] = None
    comentario_novedad: Optional[str] = None
    reporta_dano: Optional[bool] = None
    estado: Optional[bool] = None

class RetroalimentacionReserva(RetroalimentacionReservaBase):
    id_retroalimentacion: int
    creado: datetime
    actualizado: datetime

    class Config:
        from_attributes = True