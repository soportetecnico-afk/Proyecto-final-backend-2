from app.core.database import Database
from app.models.espacio import Espacio

class EspacioRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM espacio WHERE estado = TRUE ORDER BY id_espacio ASC;")
            espacios = cursor.fetchall()
            return espacios
        except Exception as e:
            raise Exception(f"Error al obtener espacios: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, espacio_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM espacio WHERE id_espacio = %s AND estado = TRUE;", (espacio_id,))
            espacio = cursor.fetchone()
            return espacio
        except Exception as e:
            raise Exception(f"Error al obtener espacio por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, espacio: Espacio):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO espacio (nombre_espacio, capacidad_aforo, ubicacion_piso, id_tipo_espacio, id_facultad, permite_sabado) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_espacio;
            """
            cursor.execute(query, (espacio.nombre_espacio, espacio.capacidad_aforo, espacio.ubicacion_piso, espacio.id_tipo_espacio, espacio.id_facultad, espacio.permite_sabado))
            nuevo_id = cursor.fetchone()['id_espacio']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear espacio: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, espacio_id: int, espacio: Espacio):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE espacio
                SET nombre_espacio = %s, capacidad_aforo = %s, ubicacion_piso = %s, id_tipo_espacio = %s, id_facultad = %s, permite_sabado = %s
                WHERE id_espacio = %s AND estado = TRUE RETURNING id_espacio;
            """
            cursor.execute(query, (espacio.nombre_espacio, espacio.capacidad_aforo, espacio.ubicacion_piso, espacio.id_tipo_espacio, espacio.id_facultad, espacio.permite_sabado, espacio_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar espacio: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, espacio_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE espacio SET estado = FALSE WHERE id_espacio = %s RETURNING id_espacio;", (espacio_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar espacio: {str(e)}")
        finally:
            conn.close()