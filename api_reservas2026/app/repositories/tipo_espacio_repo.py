from app.core.database import Database
from app.models.tipo_espacio import TipoEspacio

class TipoEspacioRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_espacio WHERE estado = TRUE ORDER BY id_tipo_espacio ASC;")
            tipos = cursor.fetchall()
            return tipos
        except Exception as e:
            raise Exception(f"Error al obtener tipos de espacio: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, tipo_espacio_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM tipo_espacio WHERE id_tipo_espacio = %s AND estado = TRUE;", (tipo_espacio_id,))
            tipo = cursor.fetchone()
            return tipo
        except Exception as e:
            raise Exception(f"Error al obtener tipo de espacio por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, tipo_espacio: TipoEspacio):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO tipo_espacio (nombre_tipo, requiere_aprobacion, color_calendario)
                VALUES (%s, %s, %s) RETURNING id_tipo_espacio;
            """
            cursor.execute(query, (tipo_espacio.nombre_tipo, tipo_espacio.requiere_aprobacion, tipo_espacio.color_calendario))
            nuevo_id = cursor.fetchone()['id_tipo_espacio']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear tipo de espacio: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, tipo_espacio_id: int, tipo_espacio: TipoEspacio):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE tipo_espacio
                SET nombre_tipo = %s, requiere_aprobacion = %s, color_calendario = %s
                WHERE id_tipo_espacio = %s AND estado = TRUE RETURNING id_tipo_espacio;
            """
            cursor.execute(query, (tipo_espacio.nombre_tipo, tipo_espacio.requiere_aprobacion, tipo_espacio.color_calendario, tipo_espacio_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar tipo de espacio: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, tipo_espacio_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE tipo_espacio SET estado = FALSE WHERE id_tipo_espacio = %s RETURNING id_tipo_espacio;", (tipo_espacio_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar tipo de espacio: {str(e)}")
        finally:
            conn.close()