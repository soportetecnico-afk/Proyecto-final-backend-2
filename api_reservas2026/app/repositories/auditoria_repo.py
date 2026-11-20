from app.core.database import Database
from app.models.auditoria import Auditoria

class AuditoriaRepository:
    """
    Repositorio de solo lectura y alta.
    'auditoria' es una tabla particionada por año que conserva la traza histórica
    del sistema, por lo que no se exponen operaciones de modificación ni borrado.
    """

    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM auditoria ORDER BY creado DESC;")
            registros = cursor.fetchall()
            return registros
        except Exception as e:
            raise Exception(f"Error al obtener auditorías: {str(e)}")
        finally:
            conn.close() # Se ejecuta siempre, haya error o no

    def obtener_por_id(self, auditoria_id: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM auditoria WHERE id_auditoria = %s;", (auditoria_id,))
            registro = cursor.fetchone()
            return registro
        except Exception as e:
            raise Exception(f"Error al obtener auditoría por ID: {str(e)}")
        finally:
            conn.close()

    def obtener_por_tabla(self, tabla_afectada: str):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM auditoria WHERE tabla_afectada = %s ORDER BY creado DESC;", (tabla_afectada,))
            registros = cursor.fetchall()
            return registros
        except Exception as e:
            raise Exception(f"Error al obtener auditorías por tabla: {str(e)}")
        finally:
            conn.close()

    def crear(self, auditoria: Auditoria):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO auditoria (id_usuario, tabla_afectada, id_registro, accion, descripcion)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_auditoria;
            """
            cursor.execute(query, (
                auditoria.id_usuario,
                auditoria.tabla_afectada,
                auditoria.id_registro,
                auditoria.accion,
                auditoria.descripcion
            ))
            nuevo_id = cursor.fetchone()['id_auditoria']
            conn.commit()
            return nuevo_id
        except Exception as e:
            conn.rollback() # Deshace cambios si hay error
            raise Exception(f"Error al crear registro de auditoría: {str(e)}")
        finally:
            conn.close()