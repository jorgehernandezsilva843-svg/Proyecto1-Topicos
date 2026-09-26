from db.database import get_connection
from models.domain import Alumno

class AlumnoRepository:
    @staticmethod
    def insertar(alumno: Alumno) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alumnos (matricula, nombre, correo, grupo, activo)
            VALUES (?, ?, ?, ?, ?)
        """, (alumno.matricula, alumno.nombre, alumno.correo, alumno.grupo, alumno.activo))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def listar_todos() -> list[Alumno]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, matricula, nombre, correo, grupo, activo FROM alumnos')
        filas = cursor.fetchall()
        conn.close()
        return [Alumno(id=f[0], matricula=f[1], nombre=f[2], correo=f[3], grupo=f[4], activo=f[5]) for f in filas]

    @staticmethod
    def actualizar(alumno: Alumno):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alumnos
            SET matricula = ?, nombre = ?, correo = ?, grupo = ?, activo = ?
            WHERE id = ?
        """, (alumno.matricula, alumno.nombre, alumno.correo, alumno.grupo, alumno.activo, alumno.id))
        conn.commit()
        conn.close()

    @staticmethod
    def cambiar_estado(alumno_id: int, nuevo_estado: int):
        """Actualiza el campo activo a 1 (activo) o 0 (inactivo)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alumnos
            SET activo = ?
            WHERE id = ?
        """, (nuevo_estado, alumno_id))
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_por_id(alumno_id: int) -> Alumno | None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, matricula, nombre, correo, grupo, activo FROM alumnos WHERE id = ?', (alumno_id,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Alumno(id=fila[0], matricula=fila[1], nombre=fila[2], correo=fila[3], grupo=fila[4], activo=fila[5])
        return None

    @staticmethod
    def eliminar_fisicamente(alumno_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alumnos WHERE id = ?', (alumno_id,))
        conn.commit()
        conn.close()
