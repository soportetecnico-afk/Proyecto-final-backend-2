import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carga .env localmente.
# En Render se utilizarán las variables configuradas en el servicio.
load_dotenv()


class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = os.getenv("DB_PORT", "5432")

    def get_connection(self):
        try:
            required = {
                "DB_HOST": self.host,
                "DB_NAME": self.database,
                "DB_USER": self.user,
                "DB_PASSWORD": self.password,
                "DB_PORT": self.port
            }

            missing = [key for key, value in required.items() if not value]

            if missing:
                raise ValueError(
                    f"Faltan variables de entorno: {', '.join(missing)}"
                )

            return psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                sslmode="require",
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )

        except Exception as e:
            print(f"Error de conexión a la BD: {e}")
            return None