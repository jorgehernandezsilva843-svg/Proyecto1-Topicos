import sqlite3
from db.database import get_connection
from models.domain import Calificacion

class CalificacionRepository:
    @staticmethod
    def registrar_calificacion(calificacion: Calificacion) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calificaciones (alumno_id, materia_id, periodo, nota)
                VALUES (?, ?, ?, ?)
            """, (calificacion.alumno_id, calificacion.materia_id, calificacion.periodo, calificacion.nota))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def actualizar_nota(calificacion_id: int, nueva_nota: float):
        """UPDATE de la nota de una calificación existente por su ID."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE calificaciones SET nota = ? WHERE id = ?
            """, (nueva_nota, calificacion_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def obtener_calificaciones_join() -> list[dict]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    c.id,
                    a.nombre AS nombre_alumno,
                    m.nombre AS nombre_materia,
                    c.periodo,
                    c.nota
                FROM calificaciones c
                INNER JOIN alumnos a ON c.alumno_id = a.id
                INNER JOIN materias m ON c.materia_id = m.id
                ORDER BY a.nombre, m.nombre
            """)
            filas = cursor.fetchall()
            return [
                {
                    'id_calificacion': f[0],
                    'nombre_alumno': f[1],
                    'nombre_materia': f[2],
                    'periodo': f[3],
                    'nota': f[4]
                }
                for f in filas
            ]
        finally:
            conn.close()

    @staticmethod
    def existe_por_alumno(alumno_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM calificaciones WHERE alumno_id = ? LIMIT 1', (alumno_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def existe_por_materia(materia_id: int) -> bool:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM calificaciones WHERE materia_id = ? LIMIT 1', (materia_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
