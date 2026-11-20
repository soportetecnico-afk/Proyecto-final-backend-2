from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReubicacionReservaBase(BaseModel):
    id_reserva: int
    id_espacio_original: int
    id_espacio_nuevo: int
    motivo_cambio: str
    estado: Optional[bool] = True

class ReubicacionReservaCrear(ReubicacionReservaBase):
    pass

class ReubicacionReservaActualizar(BaseModel):
    id_espacio_nuevo: Optional[int] = None
    motivo_cambio: Optional[str] = None
    estado: Optional[bool] = None

class ReubicacionReserva(ReubicacionReservaBase):
    id_reubicacion: int
    creado: datetime
    actualizado: datetime

    class Config:
        from_attributes = True