from app.core.database import Database

class RetroalimentacionReservaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM retroalimentacion_reserva WHERE estado = TRUE ORDER BY id_retroalimentacion ASC;")
            retroalimentaciones = cursor.fetchall()
            return retroalimentaciones
        except Exception as e:
            raise Exception(f"Error al obtener retroalimentaciones: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, retroalimentacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM retroalimentacion_reserva WHERE id_retroalimentacion = %s AND estado = TRUE;", (retroalimentacion_id,))
            retroalimentacion = cursor.fetchone()
            return retroalimentacion
        except Exception as e:
            raise Exception(f"Error al obtener retroalimentación por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, datos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO retroalimentacion_reserva (id_reserva, id_usuario_reporta, calificacion_espacio, comentario_novedad, reporta_dano)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_retroalimentacion;
            """
            cursor.execute(query, (datos.id_reserva, datos.id_usuario_reporta, datos.calificacion_espacio, datos.comentario_novedad, datos.reporta_dano))
            nuevo_id = cursor.fetchone()['id_retroalimentacion']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear retroalimentación: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, retroalimentacion_id: int, datos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE retroalimentacion_reserva
                SET calificacion_espacio = COALESCE(%s, calificacion_espacio), 
                    comentario_novedad = COALESCE(%s, comentario_novedad), 
                    reporta_dano = COALESCE(%s, reporta_dano)
                WHERE id_retroalimentacion = %s AND estado = TRUE RETURNING id_retroalimentacion;
            """
            cursor.execute(query, (datos.calificacion_espacio, datos.comentario_novedad, datos.reporta_dano, retroalimentacion_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar retroalimentación: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, retroalimentacion_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE retroalimentacion_reserva SET estado = FALSE WHERE id_retroalimentacion = %s RETURNING id_retroalimentacion;", (retroalimentacion_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar retroalimentación: {str(e)}")
        finally:
            conn.close()