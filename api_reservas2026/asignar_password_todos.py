"""Asigna una contraseña inicial a todos los usuarios de la tabla usuario.

Ejecutar desde la raíz del backend:
    python asignar_password_todos.py

Cada usuario recibe un hash scrypt con una sal aleatoria e independiente.
"""
from app.core.database import Database
from app.core.security import hash_password

PASSWORD_INICIAL = "Cul2026*"


def main():
    conn = Database().get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_usuario FROM usuario ORDER BY id_usuario;")
        usuarios = cursor.fetchall()

        if not usuarios:
            print("No hay usuarios registrados en la tabla usuario.")
            return

        for usuario in usuarios:
            usuario_id = usuario["id_usuario"] if isinstance(usuario, dict) else usuario[0]
            password_hash = hash_password(PASSWORD_INICIAL)
            cursor.execute(
                """UPDATE usuario
                   SET password_hash = %s,
                       actualizado = CURRENT_TIMESTAMP
                   WHERE id_usuario = %s;""",
                (password_hash, usuario_id),
            )

        conn.commit()
        print(f"Contraseña inicial asignada correctamente a {len(usuarios)} usuarios.")
        print("Cada usuario tiene un hash scrypt con sal independiente.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
