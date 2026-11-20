from app.core.database import Database
from app.models.facultad import Facultad

class FacultadRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todas(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM facultad WHERE estado = TRUE ORDER BY id_facultad ASC;")
            facultades = cursor.fetchall()
            return facultades
        except Exception as e:
            raise Exception(f"Error al obtener facultades: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, facultad_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM facultad WHERE id_facultad = %s AND estado = TRUE;", (facultad_id,))
            facultad = cursor.fetchone()
            return facultad
        except Exception as e:
            raise Exception(f"Error al obtener facultad por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, facultad: Facultad):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO facultad (nombre_facultad, edificio_principal, descripcion) VALUES (%s, %s, %s) RETURNING id_facultad;"
            cursor.execute(query, (facultad.nombre_facultad, facultad.edificio_principal, facultad.descripcion))
            nuevo_id = cursor.fetchone()['id_facultad']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear facultad: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, facultad_id: int, facultad: Facultad):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = "UPDATE facultad SET nombre_facultad = %s, edificio_principal = %s, descripcion = %s WHERE id_facultad = %s AND estado = TRUE RETURNING id_facultad;"
            cursor.execute(query, (facultad.nombre_facultad, facultad.edificio_principal, facultad.descripcion, facultad_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar facultad: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, facultad_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE facultad SET estado = FALSE WHERE id_facultad = %s RETURNING id_facultad;", (facultad_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar facultad: {str(e)}")
        finally:
            conn.close()