from app.core.database import Database
from app.models.usuario import UsuarioCreate, UsuarioUpdate
from app.core.security import hash_password, verify_password


class UsuarioRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        """Devuelve usuarios activos e inactivos para que el administrador pueda gestionarlos."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_usuario, nombre_completo, correo_electronico, telefono,
                       id_rol, id_facultad, estado, creado, actualizado
                FROM usuario
                ORDER BY id_usuario ASC;
            """)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener usuarios: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def obtener_por_id(self, usuario_id: int):
        """Permite consultar también usuarios inactivos para poder reactivarlos."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id_usuario, nombre_completo, correo_electronico, telefono,
                       id_rol, id_facultad, estado, creado, actualizado
                FROM usuario
                WHERE id_usuario = %s;
            """, (usuario_id,))
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al obtener usuario por ID: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def _validar_rol_oficial(cursor, id_rol: int):
        cursor.execute(
            """
            SELECT id_rol
            FROM rol
            WHERE id_rol = %s
              AND estado = TRUE
              AND LOWER(TRIM(nombre)) IN ('administrador', 'decano', 'docente');
            """,
            (id_rol,),
        )
        if cursor.fetchone() is None:
            raise ValueError(
                "El perfil seleccionado no es válido. Solo se permiten Administrador, Decano y Docente."
            )

    def crear(self, usuario: UsuarioCreate):
        """Crea un usuario guardando únicamente el hash de su contraseña."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            self._validar_rol_oficial(cursor, usuario.id_rol)
            password_hash = hash_password(usuario.password)

            cursor.execute("""
                INSERT INTO usuario (
                    nombre_completo, correo_electronico, telefono,
                    id_rol, id_facultad, estado, password_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_usuario;
            """, (
                usuario.nombre_completo,
                usuario.correo_electronico,
                usuario.telefono,
                usuario.id_rol,
                usuario.id_facultad,
                usuario.estado if usuario.estado is not None else True,
                password_hash,
            ))

            fila = cursor.fetchone()
            conn.commit()
            return fila["id_usuario"]
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear usuario: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, usuario_id: int, usuario: UsuarioUpdate):
        """
        Actualiza los datos y el estado del usuario.
        Solo cambia password_hash cuando se proporciona una contraseña nueva.
        No filtra por estado actual, de modo que también permite reactivar usuarios.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            self._validar_rol_oficial(cursor, usuario.id_rol)

            estado = usuario.estado if usuario.estado is not None else True

            if usuario.password:
                nuevo_hash = hash_password(usuario.password)
                cursor.execute("""
                    UPDATE usuario
                    SET nombre_completo = %s,
                        correo_electronico = %s,
                        telefono = %s,
                        id_rol = %s,
                        id_facultad = %s,
                        estado = %s,
                        password_hash = %s,
                        actualizado = CURRENT_TIMESTAMP
                    WHERE id_usuario = %s
                    RETURNING id_usuario;
                """, (
                    usuario.nombre_completo,
                    usuario.correo_electronico,
                    usuario.telefono,
                    usuario.id_rol,
                    usuario.id_facultad,
                    estado,
                    nuevo_hash,
                    usuario_id,
                ))
            else:
                cursor.execute("""
                    UPDATE usuario
                    SET nombre_completo = %s,
                        correo_electronico = %s,
                        telefono = %s,
                        id_rol = %s,
                        id_facultad = %s,
                        estado = %s,
                        actualizado = CURRENT_TIMESTAMP
                    WHERE id_usuario = %s
                    RETURNING id_usuario;
                """, (
                    usuario.nombre_completo,
                    usuario.correo_electronico,
                    usuario.telefono,
                    usuario.id_rol,
                    usuario.id_facultad,
                    estado,
                    usuario_id,
                ))

            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar usuario: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def autenticar(self, correo_electronico: str, password: str):
        """Autentica usuario y contraseña; el rol se obtiene desde la base de datos."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT u.id_usuario, u.nombre_completo, u.correo_electronico,
                       u.id_rol, u.id_facultad, u.password_hash, u.estado,
                       r.nombre AS nombre_rol
                FROM usuario AS u
                INNER JOIN rol AS r ON r.id_rol = u.id_rol
                WHERE LOWER(TRIM(u.correo_electronico)) = LOWER(TRIM(%s))
                  AND r.estado = TRUE
                  AND LOWER(TRIM(r.nombre)) IN ('administrador', 'decano', 'docente');
            """, (correo_electronico,))
            usuario = cursor.fetchone()

            if not usuario:
                return None
            if not verify_password(password, usuario.get("password_hash")):
                return None

            return {
                "id_usuario": usuario["id_usuario"],
                "nombre": usuario["nombre_completo"],
                "nombre_completo": usuario["nombre_completo"],
                "correo": usuario["correo_electronico"],
                "correo_electronico": usuario["correo_electronico"],
                "id_rol": usuario["id_rol"],
                "rol": usuario["nombre_rol"],
                "nombre_rol": usuario["nombre_rol"],
                "id_facultad": usuario["id_facultad"],
                "estado": bool(usuario["estado"]),
            }
        except Exception as e:
            raise Exception(f"Error al autenticar usuario: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def establecer_password(self, correo_electronico: str, password: str):
        """Guarda el hash de la contraseña para un usuario activo."""
        password_hash = hash_password(password)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE usuario
                SET password_hash = %s, actualizado = CURRENT_TIMESTAMP
                WHERE LOWER(TRIM(correo_electronico)) = LOWER(TRIM(%s))
                  AND estado = TRUE
                RETURNING id_usuario;
            """, (password_hash, correo_electronico))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al establecer contraseña: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, usuario_id: int):
        """Desactiva lógicamente un usuario."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE usuario
                SET estado = FALSE, actualizado = CURRENT_TIMESTAMP
                WHERE id_usuario = %s
                RETURNING id_usuario;
            """, (usuario_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar usuario: {str(e)}")
        finally:
            cursor.close()
            conn.close()
