from db.database import get_connection
from models.domain import Materia

class MateriaRepository:
    @staticmethod
    def insertar(materia: Materia) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO materias (clave, nombre, creditos, activo)
                VALUES (?, ?, ?, ?)
            """, (materia.clave, materia.nombre, materia.creditos, 1))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def listar_todos() -> list[Materia]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, clave, nombre, creditos, activo FROM materias')
            filas = cursor.fetchall()
            return [Materia(id=f[0], clave=f[1], nombre=f[2], creditos=f[3], activo=int(f[4])) for f in filas]
        finally:
            conn.close()

    @staticmethod
    def actualizar(materia: Materia):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE materias
                SET clave = ?, nombre = ?, creditos = ?
                WHERE id = ?
            """, (materia.clave, materia.nombre, materia.creditos, materia.id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def cambiar_estado(materia_id: int, nuevo_estado: int):
        """Actualiza el campo activo a 1 (activo) o 0 (inactivo)."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE materias SET activo = ? WHERE id = ?
            """, (nuevo_estado, materia_id))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(materia_id: int) -> Materia | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, clave, nombre, creditos, activo FROM materias WHERE id = ?', (materia_id,))
            fila = cursor.fetchone()
            if fila:
                return Materia(id=fila[0], clave=fila[1], nombre=fila[2], creditos=fila[3], activo=int(fila[4]))
            return None
        finally:
            conn.close()

    @staticmethod
    def eliminar_fisicamente(materia_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM materias WHERE id = ?', (materia_id,))
            conn.commit()
        finally:
            conn.close()
