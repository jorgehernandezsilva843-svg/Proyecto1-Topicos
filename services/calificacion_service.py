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
            
        if str(alumno.activo) == '0' or alumno.activo == 0 or str(alumno.activo).lower() == 'inactivo':
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
