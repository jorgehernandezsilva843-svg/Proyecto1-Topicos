import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'escolar.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

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
            activo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            creditos INTEGER NOT NULL,
            activo TEXT NOT NULL
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

    cursor.execute("SELECT COUNT(*) FROM usuarios_sistema")
    if cursor.fetchone()[0] == 0:
        username = 'admin'
        rol = 'administrador'
        estado = 'activo'
        password = 'admin123'
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, rol, estado))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_db()
    print("Base de datos inicializada correctamente.")
