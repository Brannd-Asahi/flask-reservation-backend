import os
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
"host": os.getenv("DB_HOST", "localhost"),

"port": int(os.getenv("DB_PORT", 3306)),
"user": os.getenv("DB_USER", "root"),
"password": os.getenv("DB_PASS", ""),
"database": os.getenv("DB_NAME", "reservas_db")
}


# Clave secreta para JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "HostalTucan@2025!")


# Opcional: lectura de host/port para app.run
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))