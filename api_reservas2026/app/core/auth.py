from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.database import Database
from app.core.security import verificar_token_acceso

_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
):
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    carga = verificar_token_acceso(credenciales.credentials)
    if not carga:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión expiró o no es válida. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    conn = Database().get_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="No fue posible conectar con la base de datos.")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT u.id_usuario, u.id_rol, u.id_facultad,
                   u.nombre_completo, u.correo_electronico, r.nombre AS nombre_rol
            FROM usuario u
            INNER JOIN rol r ON r.id_rol = u.id_rol
            WHERE u.id_usuario = %s
              AND u.estado = TRUE
              AND r.estado = TRUE
              AND r.id_rol IN (1, 3, 5)
            """,
            (int(carga["sub"]),),
        )
        usuario = cursor.fetchone()
        if not usuario or int(usuario["id_rol"]) != int(carga["id_rol"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El usuario ya no tiene una sesión autorizada.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return dict(usuario)
    finally:
        cursor.close()
        conn.close()
