from fastapi import APIRouter, Depends, HTTPException
from app.models.usuario import LoginRequest, UsuarioCreate, UsuarioUpdate
from app.repositories.usuario_repo import UsuarioRepository
from app.core.security import crear_token_acceso
from app.core.auth import obtener_usuario_actual

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])
repo = UsuarioRepository()


@router.post("/login")
def iniciar_sesion(datos: LoginRequest):
    """Valida usuario y contraseña y asigna el rol registrado en la base de datos."""
    try:
        usuario = repo.autenticar(
            correo_electronico=datos.usuario,
            password=datos.password,
        )
        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos.",
            )

        # Solo se informa que la cuenta está inactiva después de validar
        # el correo, la contraseña y el perfil seleccionado.
        if not usuario.get("estado", True):
            raise HTTPException(
                status_code=403,
                detail="Sus credenciales están inactivas. Por favor, comuníquese con el administrador de la plataforma.",
            )

        token = crear_token_acceso(usuario)
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": usuario,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="No fue posible validar el acceso.")


@router.get("/")
def listar_usuarios():
    try:
        return repo.obtener_todos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int):
    try:
        usuario = repo.obtener_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def crear_usuario(
    usuario: UsuarioCreate,
    usuario_actual: dict = Depends(obtener_usuario_actual),
):
    rol_actual = int(usuario_actual["id_rol"])
    if rol_actual not in (1, 3):
        raise HTTPException(status_code=403, detail="Solo el Administrador o el Decano pueden crear usuarios.")
    if rol_actual == 3 and int(usuario.id_rol) != 5:
        raise HTTPException(status_code=403, detail="El Decano solo puede crear usuarios con el rol Docente.")

    try:
        nuevo_id = repo.crear(usuario)
        return {"mensaje": "Usuario creado exitosamente", "id_usuario": nuevo_id}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{usuario_id}")
def actualizar_usuario(usuario_id: int, usuario: UsuarioUpdate):
    try:
        exito = repo.actualizar(usuario_id, usuario)
        if not exito:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Usuario actualizado correctamente"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    try:
        exito = repo.eliminar(usuario_id)
        if not exito:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Usuario desactivado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
