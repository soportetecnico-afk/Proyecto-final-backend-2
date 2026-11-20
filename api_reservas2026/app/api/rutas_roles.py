from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.rol import Rol
from app.repositories.rol_repo import RolRepository

router = APIRouter(prefix="/roles", tags=["Gestión de Roles"])
repo = RolRepository()


class EstadoRol(BaseModel):
    estado: bool


@router.get("/")
def listar_roles():
    try:
        # Devuelve activos e inactivos para permitir reactivación desde el frontend.
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No fue posible consultar los perfiles: {str(e)}")


@router.get("/{rol_id}")
def obtener_rol(rol_id: int):
    try:
        rol = repo.obtener_por_id(rol_id)
        if not rol:
            raise HTTPException(status_code=404, detail="Perfil no encontrado o inactivo.")
        return rol
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No fue posible consultar el perfil: {str(e)}")


@router.post("/")
def crear_rol(rol: Rol):
    try:
        nuevo_id = repo.crear(rol)
        return {"mensaje": "Perfil creado correctamente.", "id_rol": nuevo_id}
    except Exception as e:
        mensaje = str(e)
        codigo = 409 if "Ya existe" in mensaje else 400
        raise HTTPException(status_code=codigo, detail=mensaje)


@router.put("/{rol_id}")
def actualizar_rol(rol_id: int, rol: Rol):
    try:
        actualizado = repo.actualizar(rol_id, rol)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Perfil no encontrado o inactivo.")
        return {"mensaje": "Perfil actualizado correctamente."}
    except HTTPException:
        raise
    except Exception as e:
        mensaje = str(e)
        codigo = 409 if "Ya existe" in mensaje else 400
        raise HTTPException(status_code=codigo, detail=mensaje)


@router.patch("/{rol_id}/estado")
def cambiar_estado_rol(rol_id: int, datos: EstadoRol):
    if rol_id == 1 and not datos.estado:
        raise HTTPException(status_code=409, detail="El perfil Administrador principal no se puede desactivar.")
    try:
        actualizado = repo.cambiar_estado(rol_id, datos.estado)
        if not actualizado:
            raise HTTPException(status_code=404, detail="Perfil no encontrado.")
        return {
            "mensaje": "Perfil activado correctamente." if datos.estado else "Perfil desactivado correctamente.",
            "id_rol": rol_id,
            "estado": datos.estado
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rol_id}")
def eliminar_rol(rol_id: int):
    if rol_id == 1:
        raise HTTPException(status_code=409, detail="El perfil Administrador principal no se puede desactivar.")
    try:
        eliminado = repo.eliminar(rol_id)
        if not eliminado:
            raise HTTPException(status_code=404, detail="Perfil no encontrado.")
        return {"mensaje": "Perfil desactivado correctamente."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
