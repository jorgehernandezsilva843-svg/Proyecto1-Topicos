import sqlite3
from repositories.calificacion_repository import CalificacionRepository
from repositories.alumno_repository import AlumnoRepository
from models.domain import Calificacion

class CalificacionService:
    @staticmethod
    def registrar_calificacion(alumno_id: int, materia_id: int, periodo: str, nota: float) -> int:
        if not (0 <= nota <= 100):
            raise ValueError("La nota debe estar en el rango numérico de 0 a 100.")

        alumno = AlumnoRepository.obtener_por_id(alumno_id)
        if not alumno:
            raise ValueError("El alumno especificado no existe.")

        if int(alumno.activo) == 0:
            raise ValueError("No se puede registrar una calificación porque el alumno está inactivo.")

        calificacion = Calificacion(
            alumno_id=alumno_id,
            materia_id=materia_id,
            periodo=periodo,
            nota=nota
        )
        try:
            return CalificacionRepository.registrar_calificacion(calificacion)
        except sqlite3.IntegrityError:
            raise ValueError("El alumno ya tiene una calificación registrada para esa materia en ese periodo.")

    @staticmethod
    def modificar_nota(calificacion_id: int, nueva_nota: float):
        """
        Regla de negocio: la nueva nota debe estar entre 0 y 100.
        Si no lo está, lanza ValueError antes de tocar la base de datos.
        """
        if not (0 <= nueva_nota <= 100):
            raise ValueError("La nota debe estar en el rango de 0 a 100.")
        CalificacionRepository.actualizar_nota(calificacion_id, nueva_nota)

    @staticmethod
    def obtener_promedio_por_materia() -> list[tuple[str, float]]:
        return CalificacionRepository.obtener_promedio_por_materia()
