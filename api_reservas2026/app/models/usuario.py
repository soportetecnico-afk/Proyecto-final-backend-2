from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Usuario(BaseModel):
    id_usuario: Optional[int] = None
    nombre_completo: str
    correo_electronico: str
    telefono: Optional[str] = None
    id_rol: int
    id_facultad: Optional[int] = None
    estado: Optional[bool] = True


class UsuarioCreate(Usuario):
    # Para crear un usuario, la contraseña es obligatoria.
    password: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(Usuario):
    # Si no se envía una contraseña nueva, se conserva el hash actual.
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @field_validator("password", mode="before")
    @classmethod
    def convertir_password_vacia_en_none(cls, valor):
        # El formulario envía "" cuando el administrador deja el campo vacío.
        if valor == "":
            return None
        return valor


class LoginRequest(BaseModel):
    # El usuario corresponde al correo institucional registrado en la tabla usuario.
    usuario: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=256)
