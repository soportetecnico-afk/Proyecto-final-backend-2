from app.core.database import Database
from app.models.tipo_evento import TipoEvento

class TipoEventoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_evento WHERE estado = TRUE ORDER BY id_tipo_evento ASC;")
            tipos = cursor.fetchall()
            return tipos
        except Exception as e:
            raise Exception(f"Error al obtener tipos de evento: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, tipo_evento_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_evento WHERE id_tipo_evento = %s AND estado = TRUE;", (tipo_evento_id,))
            tipo = cursor.fetchone()
            return tipo
        except Exception as e:
            raise Exception(f"Error al obtener tipo de evento por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, tipo_evento: TipoEvento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO tipo_evento (nombre_evento, permite_sabado, requiere_aprobacion_especial)
                VALUES (%s, %s, %s) RETURNING id_tipo_evento;
            """
            cursor.execute(query, (tipo_evento.nombre_evento, tipo_evento.permite_sabado, tipo_evento.requiere_aprobacion_especial))
            nuevo_id = cursor.fetchone()['id_tipo_evento']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear tipo de evento: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, tipo_evento_id: int, tipo_evento: TipoEvento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE tipo_evento
                SET nombre_evento = %s, permite_sabado = %s, requiere_aprobacion_especial = %s
                WHERE id_tipo_evento = %s AND estado = TRUE RETURNING id_tipo_evento;
            """
            cursor.execute(query, (tipo_evento.nombre_evento, tipo_evento.permite_sabado, tipo_evento.requiere_aprobacion_especial, tipo_evento_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar tipo de evento: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, tipo_evento_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tipo_evento SET estado = FALSE WHERE id_tipo_evento = %s RETURNING id_tipo_evento;", (tipo_evento_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar tipo de evento: {str(e)}")
        finally:
            conn.close()