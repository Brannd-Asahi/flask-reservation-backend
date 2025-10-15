import mysql.connector
import bcrypt
import getpass
from config import DB_CONFIG

PERFIL_ADMIN_NOMBRE = "Administrador"

def crear_usuario_admin():
    conn = None
    cursor = None
    try:
        print("*** Crear usuario administrador (interactivo) ***")
        nombre_admin = input("Nombre (por defecto 'Administrador'): ") or "Administrador"
        correo_admin = input("Correo (por defecto 'admin@hostaltucan.com'): ") or "admin@hostaltucan.com"

        # Solicita la contraseña sin mostrarla en pantalla
        clave_admin = getpass.getpass("Contraseña para el administrador (no se mostrará): ")
        if not clave_admin:
            print("Contraseña vacía. Abortando.")
            return

        # Se conecta a la base de datos usando DB_CONFIG
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verifica que exista el perfil 'Administrador'
        cursor.execute("SELECT id FROM perfil WHERE nombre = %s", (PERFIL_ADMIN_NOMBRE,))
        perfil_id_row = cursor.fetchone()
        if perfil_id_row is None:
            print("Error: El perfil 'Administrador' no existe en la tabla perfil. Crear el perfil antes de ejecutar.")
            return
        perfil_id = perfil_id_row[0]

        # Verifica si ya existe un usuario con ese correo
        cursor.execute("SELECT ID FROM usuario WHERE correo = %s", (correo_admin,))
        if cursor.fetchone() is not None:
            print("Error: Ya existe un usuario con ese correo.")
            return

        # Hashea la contraseña y la guarda como texto UTF-8
        clave_hash = bcrypt.hashpw(clave_admin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Inserta el usuario administrador
        query = """
        INSERT INTO usuario (nombre, correo, clave, perfil_id)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre_admin, correo_admin, clave_hash, perfil_id))
        conn.commit()
        print("Usuario administrador creado con éxito.")

    except mysql.connector.Error as err:
        print("Error al crear el usuario:", err)

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

if __name__ == "__main__":
    crear_usuario_admin()
