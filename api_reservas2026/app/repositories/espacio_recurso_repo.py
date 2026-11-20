from app.core.database import Database
from app.models.espacio_recurso import EspacioRecurso

class EspacioRecursoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todas(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM espacio_recurso WHERE estado = TRUE ORDER BY id_espacio_recurso ASC;")
            asignaciones = cursor.fetchall()
            return asignaciones
        except Exception as e:
            raise Exception(f"Error al obtener asignaciones de recursos: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, espacio_recurso_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM espacio_recurso WHERE id_espacio_recurso = %s AND estado = TRUE;", (espacio_recurso_id,))
            asignacion = cursor.fetchone()
            return asignacion
        except Exception as e:
            raise Exception(f"Error al obtener asignación por ID: {str(e)}")
        finally:
            conn.close()

    def obtener_por_espacio(self, espacio_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT er.id_espacio_recurso, er.id_espacio, er.id_recurso, er.cantidad_asignada,
                       r.nombre_recurso, r.categoria, r.estado_mantenimiento
                FROM espacio_recurso er
                JOIN recurso r ON r.id_recurso = er.id_recurso
                WHERE er.id_espacio = %s AND er.estado = TRUE AND r.estado = TRUE
                ORDER BY r.nombre_recurso ASC;
            """
            cursor.execute(query, (espacio_id,))
            recursos = cursor.fetchall()
            return recursos
        except Exception as e:
            raise Exception(f"Error al obtener recursos por espacio: {str(e)}")
        finally:
            conn.close()

    def crear(self, espacio_recurso: EspacioRecurso):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO espacio_recurso (id_espacio, id_recurso, cantidad_asignada)
                VALUES (%s, %s, %s) RETURNING id_espacio_recurso;
            """
            cursor.execute(query, (espacio_recurso.id_espacio, espacio_recurso.id_recurso, espacio_recurso.cantidad_asignada))
            nuevo_id = cursor.fetchone()['id_espacio_recurso']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear asignación de recurso: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, espacio_recurso_id: int, espacio_recurso: EspacioRecurso):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE espacio_recurso
                SET id_espacio = %s, id_recurso = %s, cantidad_asignada = %s
                WHERE id_espacio_recurso = %s AND estado = TRUE RETURNING id_espacio_recurso;
            """
            cursor.execute(query, (espacio_recurso.id_espacio, espacio_recurso.id_recurso, espacio_recurso.cantidad_asignada, espacio_recurso_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar asignación de recurso: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, espacio_recurso_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE espacio_recurso SET estado = FALSE WHERE id_espacio_recurso = %s RETURNING id_espacio_recurso;", (espacio_recurso_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar asignación de recurso: {str(e)}")
        finally:
            conn.close()