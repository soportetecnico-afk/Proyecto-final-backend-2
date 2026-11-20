from app.core.database import Database
from app.models.reserva import Reserva

class ReservaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_capacidad_espacio(self, id_espacio: int):
        """Devuelve el aforo máximo registrado para un espacio."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id_espacio, nombre_espacio, capacidad_aforo
                FROM espacio
                WHERE id_espacio = %s;
                """,
                (id_espacio,),
            )
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al consultar la capacidad del espacio: {str(e)}") from e
        finally:
            cursor.close()
            conn.close()

    def obtener_todas(self, usuario_actual: dict):
        """Docente consulta solo sus reservas; Administrador y Decano consultan todas."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            if int(usuario_actual["id_rol"]) == 5:
                cursor.execute(
                    """
                    SELECT r.*,
                           u.nombre_completo AS nombre_solicitante,
                           u.correo_electronico AS correo_solicitante
                    FROM reserva r
                    LEFT JOIN usuario u ON u.id_usuario = r.id_usuario
                    WHERE r.estado = TRUE AND r.id_usuario = %s
                    ORDER BY r.id_reserva DESC;
                    """,
                    (int(usuario_actual["id_usuario"]),),
                )
            else:
                cursor.execute(
                    """
                    SELECT r.*,
                           u.nombre_completo AS nombre_solicitante,
                           u.correo_electronico AS correo_solicitante
                    FROM reserva r
                    LEFT JOIN usuario u ON u.id_usuario = r.id_usuario
                    WHERE r.estado = TRUE
                    ORDER BY r.id_reserva DESC;
                    """
                )
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error al obtener reservas: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def obtener_por_id(self, reserva_id: int, usuario_actual: dict):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            if int(usuario_actual["id_rol"]) == 5:
                cursor.execute(
                    """
                    SELECT r.*,
                           u.nombre_completo AS nombre_solicitante,
                           u.correo_electronico AS correo_solicitante
                    FROM reserva r
                    LEFT JOIN usuario u ON u.id_usuario = r.id_usuario
                    WHERE r.id_reserva = %s
                      AND r.id_usuario = %s
                      AND r.estado = TRUE;
                    """,
                    (reserva_id, int(usuario_actual["id_usuario"])),
                )
            else:
                cursor.execute(
                    """
                    SELECT r.*,
                           u.nombre_completo AS nombre_solicitante,
                           u.correo_electronico AS correo_solicitante
                    FROM reserva r
                    LEFT JOIN usuario u ON u.id_usuario = r.id_usuario
                    WHERE r.id_reserva = %s AND r.estado = TRUE;
                    """,
                    (reserva_id,),
                )
            return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Error al obtener reserva por ID: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def crear(self, reserva: Reserva):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO reserva
                (id_usuario, id_espacio, id_tipo_evento, id_aprobador, fecha_reserva, hora_inicio,
                 hora_fin, cantidad_asistentes, estado_reserva, fecha_limite_aprobacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_reserva;
            """
            cursor.execute(query, (
                reserva.id_usuario, reserva.id_espacio, reserva.id_tipo_evento, reserva.id_aprobador,
                reserva.fecha_reserva, reserva.hora_inicio, reserva.hora_fin,
                reserva.cantidad_asistentes, reserva.estado_reserva, reserva.fecha_limite_aprobacion
            ))
            nuevo_id = cursor.fetchone()['id_reserva']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear reserva: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, reserva_id: int, reserva: Reserva):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE reserva
                SET id_usuario = %s, id_espacio = %s, id_tipo_evento = %s, id_aprobador = %s,
                    fecha_reserva = %s, hora_inicio = %s, hora_fin = %s, cantidad_asistentes = %s,
                    estado_reserva = %s, fecha_limite_aprobacion = %s
                WHERE id_reserva = %s AND estado = TRUE
                RETURNING id_reserva;
            """
            cursor.execute(query, (
                reserva.id_usuario, reserva.id_espacio, reserva.id_tipo_evento, reserva.id_aprobador,
                reserva.fecha_reserva, reserva.hora_inicio, reserva.hora_fin,
                reserva.cantidad_asistentes, reserva.estado_reserva, reserva.fecha_limite_aprobacion,
                reserva_id
            ))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar reserva: {str(e)}")
        finally:
            conn.close()


    def resolver_decision(
        self,
        reserva_id: int,
        id_administrador: int,
        decision: str,
        motivo_rechazo: str | None = None,
    ):
        """Aprueba o rechaza una reserva pendiente y registra al administrador."""
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("No fue posible conectar con PostgreSQL.")

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE reserva
                   SET estado_reserva = %s,
                       id_aprobador = %s,
                       motivo_rechazo = %s
                 WHERE id_reserva = %s
                   AND estado = TRUE
                   AND LOWER(TRIM(estado_reserva)) = 'pendiente'
                RETURNING id_reserva;
                """,
                (decision, id_administrador, motivo_rechazo, reserva_id),
            )
            actualizado = cursor.fetchone()
            if actualizado is None:
                conn.rollback()
                return False

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Error SQL al registrar la decisión: {e}") from e
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, reserva_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE reserva SET estado = FALSE WHERE id_reserva = %s RETURNING id_reserva;", (reserva_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar reserva: {str(e)}")
        finally:
            conn.close()