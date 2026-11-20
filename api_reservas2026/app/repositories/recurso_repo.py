from app.core.database import Database
from app.models.recurso import Recurso

class RecursoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM recurso WHERE estado = TRUE ORDER BY id_recurso ASC;")
            recursos = cursor.fetchall()
            return recursos
        except Exception as e:
            raise Exception(f"Error al obtener recursos: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, recurso_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM recurso WHERE id_recurso = %s AND estado = TRUE;", (recurso_id,))
            recurso = cursor.fetchone()
            return recurso
        except Exception as e:
            raise Exception(f"Error al obtener recurso por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, recurso: Recurso):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO recurso (nombre_recurso, categoria, estado_mantenimiento)
                VALUES (%s, %s, %s) RETURNING id_recurso;
            """
            cursor.execute(query, (recurso.nombre_recurso, recurso.categoria, recurso.estado_mantenimiento))
            nuevo_id = cursor.fetchone()['id_recurso']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear recurso: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, recurso_id: int, recurso: Recurso):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE recurso
                SET nombre_recurso = %s, categoria = %s, estado_mantenimiento = %s
                WHERE id_recurso = %s AND estado = TRUE RETURNING id_recurso;
            """
            cursor.execute(query, (recurso.nombre_recurso, recurso.categoria, recurso.estado_mantenimiento, recurso_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar recurso: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, recurso_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE recurso SET estado = FALSE WHERE id_recurso = %s RETURNING id_recurso;", (recurso_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar recurso: {str(e)}")
        finally:
            conn.close()