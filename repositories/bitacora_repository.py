import sqlite3
from db.database import get_connection

class BitacoraRepository:
    @staticmethod
    def registrar_accion(usuario_id: int, accion: str):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bitacora (usuario_id, accion)
                VALUES (?, ?)
            """, (usuario_id, accion))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def listar_acciones() -> list[dict]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.id, u.username, b.accion, b.fecha
                FROM bitacora b
                INNER JOIN usuarios_sistema u ON b.usuario_id = u.id
                ORDER BY b.fecha DESC
            """)
            filas = cursor.fetchall()
            return [
                {
                    'id': f[0],
                    'username': f[1],
                    'accion': f[2],
                    'fecha': f[3]
                }
                for f in filas
            ]
        finally:
            conn.close()
