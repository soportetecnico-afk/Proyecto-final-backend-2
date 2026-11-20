from app.core.database import Database
from app.models.bloqueo_mantenimiento import BloqueoMantenimiento

class BloqueoMantenimientoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM bloqueo_mantenimiento WHERE estado = TRUE ORDER BY fecha_inicio DESC;")
            bloqueos = cursor.fetchall()
            return bloqueos
        except Exception as e:
            raise Exception(f"Error al obtener bloqueos: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, bloqueo_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM bloqueo_mantenimiento WHERE id_bloqueo = %s AND estado = TRUE;", (bloqueo_id,))
            bloqueo = cursor.fetchone()
            return bloqueo
        except Exception as e:
            raise Exception(f"Error al obtener bloqueo por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, bloqueo: BloqueoMantenimiento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO bloqueo_mantenimiento
                (id_espacio, id_usuario_reporta, fecha_inicio, fecha_fin, tipo_bloqueo, descripcion)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_bloqueo;
            """
            cursor.execute(query, (
                bloqueo.id_espacio,
                bloqueo.id_usuario_reporta,
                bloqueo.fecha_inicio,
                bloqueo.fecha_fin,
                bloqueo.tipo_bloqueo,
                bloqueo.descripcion
            ))
            nuevo_id = cursor.fetchone()['id_bloqueo']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback() # Deshace cambios si hay error
            raise Exception(f"Error al crear bloqueo: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, bloqueo_id: int, bloqueo: BloqueoMantenimiento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE bloqueo_mantenimiento
                SET id_espacio = %s, id_usuario_reporta = %s, fecha_inicio = %s,
                    fecha_fin = %s, tipo_bloqueo = %s, descripcion = %s
                WHERE id_bloqueo = %s AND estado = TRUE
                RETURNING id_bloqueo;
            """
            cursor.execute(query, (
                bloqueo.id_espacio, bloqueo.id_usuario_reporta, bloqueo.fecha_inicio,
                bloqueo.fecha_fin, bloqueo.tipo_bloqueo, bloqueo.descripcion, bloqueo_id
            ))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar bloqueo: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, bloqueo_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE bloqueo_mantenimiento SET estado = FALSE WHERE id_bloqueo = %s RETURNING id_bloqueo;", (bloqueo_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar bloqueo: {str(e)}")
        finally:
            conn.close()