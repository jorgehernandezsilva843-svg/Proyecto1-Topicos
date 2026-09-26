from db.database import get_connection
from models.domain import Materia

class MateriaRepository:
    @staticmethod
    def insertar(materia: Materia) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO materias (clave, nombre, creditos, activo)
            VALUES (?, ?, ?, ?)
        """, (materia.clave, materia.nombre, materia.creditos, materia.activo))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def listar_todos() -> list[Materia]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, clave, nombre, creditos, activo FROM materias')
        filas = cursor.fetchall()
        conn.close()
        return [Materia(id=f[0], clave=f[1], nombre=f[2], creditos=f[3], activo=f[4]) for f in filas]

    @staticmethod
    def actualizar(materia: Materia):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE materias
            SET clave = ?, nombre = ?, creditos = ?, activo = ?
            WHERE id = ?
        """, (materia.clave, materia.nombre, materia.creditos, materia.activo, materia.id))
        conn.commit()
        conn.close()

    @staticmethod
    def desactivar(materia_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE materias
            SET activo = 0
            WHERE id = ?
        """, (materia_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def eliminar_fisicamente(materia_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM materias WHERE id = ?', (materia_id,))
        conn.commit()
        conn.close()
