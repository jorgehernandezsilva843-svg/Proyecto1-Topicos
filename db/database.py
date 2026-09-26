import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'escolar.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            activo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            grupo TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            creditos INTEGER NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            periodo TEXT NOT NULL,
            nota REAL NOT NULL,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias (id) ON DELETE CASCADE,
            UNIQUE(alumno_id, materia_id, periodo)
        )
    """)

    # Insertar usuarios por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios_sistema")
    if cursor.fetchone()[0] == 0:
        usuarios_default = [
            ('admin',   _hash('admin123'),   'administrador', 'activo'),
            ('maestro', _hash('maestro123'), 'operador',      'activo'),
        ]
        cursor.executemany("""
            INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
            VALUES (?, ?, ?, ?)
        """, usuarios_default)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_db()
    print("Base de datos inicializada correctamente.")
