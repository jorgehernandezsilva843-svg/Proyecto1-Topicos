import sqlite3
from db.database import get_connection
from models.domain import Calificacion

class CalificacionRepository:
    @staticmethod
    def registrar_calificacion(calificacion: Calificacion) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calificaciones (alumno_id, materia_id, periodo, nota)
            VALUES (?, ?, ?, ?)
        """, (calificacion.alumno_id, calificacion.materia_id, calificacion.periodo, calificacion.nota))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def obtener_calificaciones_join() -> list[dict]:
        conn = get_connection()
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
        """)
        filas = cursor.fetchall()
        conn.close()
        
        resultados = []
        for f in filas:
            resultados.append({
                'id_calificacion': f[0],
                'nombre_alumno': f[1],
                'nombre_materia': f[2],
                'periodo': f[3],
                'nota': f[4]
            })
        return resultados

    @staticmethod
    def existe_por_alumno(alumno_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM calificaciones WHERE alumno_id = ? LIMIT 1', (alumno_id,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe

    @staticmethod
    def existe_por_materia(materia_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM calificaciones WHERE materia_id = ? LIMIT 1', (materia_id,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe
