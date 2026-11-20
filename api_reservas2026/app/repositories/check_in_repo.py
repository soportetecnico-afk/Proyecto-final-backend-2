from app.core.database import Database
from app.models.check_in import CheckIn

class CheckInRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM check_in WHERE estado = TRUE ORDER BY id_check_in DESC;")
            check_ins = cursor.fetchall()
            return check_ins
        except Exception as e:
            raise Exception(f"Error al obtener check-ins: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, check_in_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM check_in WHERE id_check_in = %s AND estado = TRUE;", (check_in_id,))
            check_in = cursor.fetchone()
            return check_in
        except Exception as e:
            raise Exception(f"Error al obtener check-in por ID: {str(e)}")
        finally:
            conn.close()

    def obtener_por_reserva(self, reserva_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM check_in WHERE id_reserva = %s AND estado = TRUE;", (reserva_id,))
            check_in = cursor.fetchone()
            return check_in
        except Exception as e:
            raise Exception(f"Error al obtener check-in por reserva: {str(e)}")
        finally:
            conn.close()

    def crear(self, check_in: CheckIn):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO check_in (id_reserva, hora_ingreso_real, estado_asistencia)
                VALUES (%s, %s, %s) RETURNING id_check_in;
            """
            cursor.execute(query, (check_in.id_reserva, check_in.hora_ingreso_real, check_in.estado_asistencia))
            nuevo_id = cursor.fetchone()['id_check_in']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear check-in: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, check_in_id: int, check_in: CheckIn):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE check_in
                SET id_reserva = %s, hora_ingreso_real = %s, estado_asistencia = %s
                WHERE id_check_in = %s AND estado = TRUE RETURNING id_check_in;
            """
            cursor.execute(query, (check_in.id_reserva, check_in.hora_ingreso_real, check_in.estado_asistencia, check_in_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar check-in: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, check_in_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE check_in SET estado = FALSE WHERE id_check_in = %s RETURNING id_check_in;", (check_in_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar check-in: {str(e)}")
        finally:
            conn.close()