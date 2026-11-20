from app.core.database import Database
from app.models.modulo import Modulo

class ModuloRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM modulo WHERE estado = TRUE ORDER BY id_modulo ASC;")
            modulos = cursor.fetchall()
            return modulos
        except Exception as e:
            raise Exception(f"Error al obtener módulos: {str(e)}")
        finally:
            conn.close()

    def obtener_por_id(self, modulo_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM modulo WHERE id_modulo = %s AND estado = TRUE;", (modulo_id,))
            modulo = cursor.fetchone()
            return modulo
        except Exception as e:
            raise Exception(f"Error al obtener módulo por ID: {str(e)}")
        finally:
            conn.close()

    def crear(self, modulo: Modulo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO modulo (nombre, ruta_url) VALUES (%s, %s) RETURNING id_modulo;"
            cursor.execute(query, (modulo.nombre, modulo.ruta_url))
            nuevo_id = cursor.fetchone()['id_modulo']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al crear módulo: {str(e)}")
        finally:
            conn.close()

    def actualizar(self, modulo_id: int, modulo: Modulo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = "UPDATE modulo SET nombre = %s, ruta_url = %s WHERE id_modulo = %s AND estado = TRUE RETURNING id_modulo;"
            cursor.execute(query, (modulo.nombre, modulo.ruta_url, modulo_id))
            actualizado = cursor.fetchone()
            conn.commit()
            return actualizado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al actualizar módulo: {str(e)}")
        finally:
            conn.close()

    def eliminar(self, modulo_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE modulo SET estado = FALSE WHERE id_modulo = %s RETURNING id_modulo;", (modulo_id,))
            eliminado = cursor.fetchone()
            conn.commit()
            return eliminado is not None
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error al eliminar módulo: {str(e)}")
        finally:
            conn.close()