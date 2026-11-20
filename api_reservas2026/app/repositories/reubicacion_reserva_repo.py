from app.core.database import Database

class ReubicacionReservaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM reubicacion_reserva WHERE estado = TRUE ORDER BY id_reubicacion ASC;")
            reubicaciones = cursor.fetchall()
            return reubicaciones
        except Exception as e:
            raise Exception(f"Error al obtener reubicaciones: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, reubicacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM reubicacion_reserva WHERE id_reubicacion = %s AND estado = TRUE;", (reubicacion_id,))
            reubicacion = cursor.fetchone()
            return reubicacion
        except Exception as e:
            raise Exception(f"Error al obtener reubicación por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, datos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO reubicacion_reserva (id_reserva, id_espacio_original, id_espacio_nuevo, motivo_cambio)
                VALUES (%s, %s, %s, %s) RETURNING id_reubicacion;
            """
            cursor.execute(query, (datos.id_reserva, datos.id_espacio_original, datos.id_espacio_nuevo, datos.motivo_cambio))
            nuevo_id = cursor.fetchone()['id_reubicacion']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear reubicación: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, reubicacion_id: int, datos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE reubicacion_reserva
                SET id_espacio_nuevo = COALESCE(%s, id_espacio_nuevo), 
                    motivo_cambio = COALESCE(%s, motivo_cambio)
                WHERE id_reubicacion = %s AND estado = TRUE RETURNING id_reubicacion;
            """
            cursor.execute(query, (datos.id_espacio_nuevo, datos.motivo_cambio, reubicacion_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar reubicación: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, reubicacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE reubicacion_reserva SET estado = FALSE WHERE id_reubicacion = %s RETURNING id_reubicacion;", (reubicacion_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar reubicación: {str(e)}")
        finally:
            conn.close()