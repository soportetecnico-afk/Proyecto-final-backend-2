from app.core.database import Database
from app.models.notificacion import Notificacion

class NotificacionRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todas(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM notificacion WHERE estado = TRUE ORDER BY id_notificacion DESC;")
            notificaciones = cursor.fetchall()
            return notificaciones
        except Exception as e:
            raise Exception(f"Error al obtener notificaciones: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, notificacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM notificacion WHERE id_notificacion = %s AND estado = TRUE;", (notificacion_id,))
            notificacion = cursor.fetchone()
            return notificacion
        except Exception as e:
            raise Exception(f"Error al obtener notificación por ID: {str(e)}")
        finally:
            conn.close()

    def obtener_por_usuario(self, usuario_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM notificacion WHERE id_usuario = %s AND estado = TRUE ORDER BY creado DESC;", (usuario_id,))
            notificaciones = cursor.fetchall()
            return notificaciones
        except Exception as e:
            raise Exception(f"Error al obtener notificaciones de usuario: {str(e)}")
        finally:
            conn.close()

    def crear(self, notificacion: Notificacion):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO notificacion (id_usuario, id_reserva, tipo_canal, mensaje_texto, enviada)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_notificacion;
            """
            cursor.execute(query, (
                notificacion.id_usuario,
                notificacion.id_reserva,
                notificacion.tipo_canal,
                notificacion.mensaje_texto,
                notificacion.enviada
            ))
            nuevo_id = cursor.fetchone()['id_notificacion']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear notificación: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, notificacion_id: int, notificacion: Notificacion):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE notificacion
                SET id_usuario = %s, id_reserva = %s, tipo_canal = %s, mensaje_texto = %s, enviada = %s
                WHERE id_notificacion = %s AND estado = TRUE RETURNING id_notificacion;
            """
            cursor.execute(query, (
                notificacion.id_usuario, notificacion.id_reserva, notificacion.tipo_canal,
                notificacion.mensaje_texto, notificacion.enviada, notificacion_id
            ))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar notificación: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, notificacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE notificacion SET estado = FALSE WHERE id_notificacion = %s RETURNING id_notificacion;", (notificacion_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar notificación: {str(e)}")
        finally:
            conn.close()