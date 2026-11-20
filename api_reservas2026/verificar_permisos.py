from app.core.database import Database

db = Database()
conn = db.get_connection()

if conn is None:
    print("Error: no se pudo conectar a PostgreSQL.")
    exit()

cursor = conn.cursor()

try:
    cursor.execute("""
        SELECT
            current_database() AS base_datos,
            current_user AS usuario,
            inet_server_addr() AS servidor,
            inet_server_port() AS puerto;
    """)

    print("\n--- BASE DE DATOS UTILIZADA POR FASTAPI ---")
    print(cursor.fetchone())

    cursor.execute("""
        SELECT
            mr.id_modulosxrol,
            mr.id_rol,
            mr.id_modulo,
            m.nombre,
            mr.estado AS permiso_activo
        FROM modulosxrol mr
        INNER JOIN modulo m
            ON m.id_modulo = mr.id_modulo
        WHERE mr.id_rol = 3
          AND mr.id_modulo = 18
        ORDER BY mr.id_modulosxrol DESC;
    """)

    print("\n--- PERMISO DEL DECANO ---")
    print(cursor.fetchall())

finally:
    cursor.close()
    conn.close()