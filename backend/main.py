from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt
import mysql.connector
from mysql.connector import Error
import json
from config import DB_CONFIG, JWT_SECRET_KEY, FLASK_HOST, FLASK_PORT
from datetime import timedelta, datetime
import re

from flask_cors import CORS   

app = Flask(__name__)
CORS(app)                     
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
jwt = JWTManager(app)

def get_connection():
    """Devuelve una conexión a la base de datos usando DB_CONFIG."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG.get("host", "localhost"),
            port=DB_CONFIG.get("port", 3306),
            user=DB_CONFIG.get("user", "root"),
            password=DB_CONFIG.get("password", ""),
            database=DB_CONFIG.get("database", "")
        )
        return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


def parse_identity():
    """
    Normaliza el identity del JWT.
    Devuelve siempre un dict (vacío si no se puede parsear).
    """
    raw = get_jwt_identity()
    if raw is None:
        return {}
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    if isinstance(raw, dict):
        return raw
    return {}


def is_valid_email(email: str) -> bool:
    """Validación simple de email (no exhaustiva)."""
    if not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_date_yyyy_mm_dd(date_str: str) -> bool:
    """Verifica formato YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except Exception:
        return False


@app.route('/login', methods=['POST'])
def login():
    """Valida credenciales y devuelve un access_token."""
    data = request.get_json()
    if not data or 'correo' not in data or 'clave' not in data:
        return jsonify({"msg": "Correo y clave son obligatorios"}), 400

    correo = data['correo']
    clave = data['clave']

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(clave.encode('utf-8'), user['clave'].encode('utf-8')):
            # Se guarda el identity como string JSON para consistencia
            identity_obj = {'ID': user['ID'], 'correo': user['correo'], 'perfil_id': user['perfil_id']}
            access_token = create_access_token(identity=json.dumps(identity_obj))
            return jsonify({"access_token": access_token}), 200
        return jsonify({"msg": "Correo o clave incorrectos"}), 401
    except Error as e:
        return jsonify({"msg": f"Error al realizar el login: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/usuarios', methods=['POST'])
@jwt_required()
def create_user_with_token():
    """Crea usuario (solo admin: perfil_id == 1)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') != 1:
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403

    data = request.get_json()
    if not data or 'correo' not in data or 'clave' not in data or 'perfil_id' not in data or 'nombre' not in data:
        return jsonify({"msg": "Faltan datos obligatorios (correo, clave, perfil_id, nombre)"}), 400

    correo = data['correo']
    clave = data['clave']
    perfil_id = data['perfil_id']
    nombre = data['nombre']

    # Validación mínima de email
    if not is_valid_email(correo):
        return jsonify({"msg": "El correo no tiene un formato válido"}), 400

    hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM usuario WHERE correo = %s", (correo,))
        if cursor.fetchone() is not None:
            return jsonify({"msg": "El correo ya está registrado"}), 409

        cursor.execute("INSERT INTO usuario (correo, clave, nombre, perfil_id) VALUES (%s, %s, %s, %s)",
                       (correo, hashed_password, nombre, perfil_id))
        conn.commit()
        return jsonify({"msg": "Usuario creado exitosamente"}), 201
    except Error as e:
        return jsonify({"msg": f"Error al crear usuario: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    """Lista usuarios (solo admin)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') != 1:
        return jsonify({"msg": "No tienes permisos para listar usuarios"}), 403

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.nombre, u.correo, p.nombre AS perfil
            FROM usuario u
            JOIN perfil p ON u.perfil_id = p.ID
        """)
        usuarios = cursor.fetchall()
        return jsonify(usuarios), 200
    except Error as e:
        return jsonify({"msg": f"Error al obtener usuarios: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def editar_usuario(id):
    """Edita usuario (solo admin)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') != 1:
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403

    data = request.get_json()
    if not data or ('correo' not in data and 'nombre' not in data and 'clave' not in data and 'perfil_id' not in data):
        return jsonify({"msg": "Faltan datos para actualizar"}), 400

    correo = data.get('correo')
    nombre = data.get('nombre')
    clave = data.get('clave')
    perfil_id = data.get('perfil_id')

    hashed_password = None
    if clave:
        hashed_password = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        query = "UPDATE usuario SET "
        params = []

        if correo:
            query += "correo = %s, "
            params.append(correo)
        if nombre:
            query += "nombre = %s, "
            params.append(nombre)
        if hashed_password:
            query += "clave = %s, "
            params.append(hashed_password)
        if perfil_id:
            query += "perfil_id = %s, "
            params.append(perfil_id)

        query = query.rstrip(', ')
        query += " WHERE ID = %s"
        params.append(id)

        cursor.execute(query, tuple(params))
        conn.commit()
        return jsonify({"msg": "Usuario actualizado exitosamente"}), 200
    except Error as e:
        return jsonify({"msg": f"Error al editar usuario: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/reservas', methods=['POST'])
@jwt_required()
def registrar_reserva():
    """Registra reserva (solo empleado: perfil_id == 3)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') != 3:
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403

    data = request.get_json()
    if not data or 'fecha' not in data or 'cliente_id' not in data:
        return jsonify({"msg": "Faltan datos obligatorios (fecha, cliente_id)"}), 400

    fecha = data['fecha']
    cliente_id = data['cliente_id']
    supervisor_id = data.get('supervisor_id')

    # Validar formato de fecha básico YYYY-MM-DD
    if not is_valid_date_yyyy_mm_dd(fecha):
        return jsonify({"msg": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        if supervisor_id:
            cursor.execute("INSERT INTO reserva (fecha, cliente_id, supervisor_id) VALUES (%s, %s, %s)",
                           (fecha, cliente_id, supervisor_id))
        else:
            cursor.execute("INSERT INTO reserva (fecha, cliente_id) VALUES (%s, %s)",
                           (fecha, cliente_id))
        conn.commit()
        return jsonify({"msg": "Reserva registrada exitosamente"}), 201
    except Error as e:
        return jsonify({"msg": f"Error al registrar reserva: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/reservas', methods=['GET'])
@jwt_required()
def consultar_reservas():
    """Consulta reservas (supervisor, empleado o cliente)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') not in [2, 3, 4]:
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.ID, r.fecha, c.nombre AS cliente, s.nombre AS supervisor
            FROM reserva r
            JOIN cliente c ON r.cliente_id = c.ID
            LEFT JOIN supervisor s ON r.supervisor_id = s.ID
        """)
        reservas = cursor.fetchall()
        return jsonify(reservas), 200
    except Error as e:
        return jsonify({"msg": f"Error al consultar reservas: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


@app.route('/reservas/<int:id>', methods=['PUT'])
@jwt_required()
def editar_reserva(id):
    """Edita reserva (supervisor o empleado)."""
    user_data = parse_identity()
    if user_data.get('perfil_id') not in [2, 3]:
        return jsonify({"msg": "No tienes permiso para realizar esta acción"}), 403

    data = request.get_json()
    if 'fecha' not in data:
        return jsonify({"msg": "Falta la fecha para actualizar"}), 400

    fecha = data['fecha']
    if not is_valid_date_yyyy_mm_dd(fecha):
        return jsonify({"msg": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"msg": "Error al conectar con la base de datos"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE reserva SET fecha = %s WHERE ID = %s", (fecha, id))
        conn.commit()
        return jsonify({"msg": "Reserva actualizada exitosamente"}), 200
    except Error as e:
        return jsonify({"msg": f"Error al editar reserva: {e}"}), 500
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None and getattr(conn, 'is_connected', lambda: True)():
            try:
                conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT)
