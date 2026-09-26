import sqlite3
from repositories.calificacion_repository import CalificacionRepository
from repositories.alumno_repository import AlumnoRepository
from repositories.materia_repository import MateriaRepository
from models.domain import Calificacion

class CalificacionService:
    @staticmethod
    def validar_periodo(periodo: str):
        import re
        if not re.match(r"^(febrero-junio|agosto-diciembre)\s+\d{4}$", periodo.strip().lower()):
            raise ValueError("El periodo debe tener el formato 'febrero-junio YYYY' o 'agosto-diciembre YYYY'.")

    @staticmethod
    def registrar_calificacion(alumno_id: int, materia_id: int, periodo: str, nota: float, usuario_id: int = 0) -> int:
        CalificacionService.validar_periodo(periodo)
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
            from repositories.bitacora_repository import BitacoraRepository
            id_insertado = CalificacionRepository.registrar_calificacion(calificacion)
            materia = MateriaRepository.obtener_por_id(materia_id)
            BitacoraRepository.registrar_accion(usuario_id, f"Registró la calificación de {nota} para el alumno {alumno.matricula} en {materia.nombre} ({periodo})")
            return id_insertado
        except sqlite3.IntegrityError:
            raise ValueError("El alumno ya tiene una calificación registrada para esa materia en ese periodo.")

    @staticmethod
    def modificar_calificacion(calificacion_id: int, alumno_id: int, materia_id: int, periodo: str, nota: float, usuario_id: int = 0):
        CalificacionService.validar_periodo(periodo)
        if not (0 <= nota <= 100):
            raise ValueError("La nota debe estar en el rango de 0 a 100.")

        alumno = AlumnoRepository.obtener_por_id(alumno_id)
        if not alumno:
            raise ValueError("El alumno especificado no existe.")

        if int(alumno.activo) == 0:
            raise ValueError("No se puede actualizar una calificación porque el alumno está inactivo.")

        calificacion = Calificacion(
            id=calificacion_id,
            alumno_id=alumno_id,
            materia_id=materia_id,
            periodo=periodo,
            nota=nota
        )
        try:
            from repositories.bitacora_repository import BitacoraRepository
            CalificacionRepository.actualizar(calificacion)
            materia = MateriaRepository.obtener_por_id(materia_id)
            BitacoraRepository.registrar_accion(usuario_id, f"Actualizó la calificación a {nota} para el alumno {alumno.matricula} en {materia.nombre} ({periodo})")
        except sqlite3.IntegrityError:
            raise ValueError("El alumno ya tiene una calificación registrada para esa materia en ese periodo.")

    @staticmethod
    def obtener_promedio_por_materia() -> list[tuple[str, float]]:
        return CalificacionRepository.obtener_promedio_por_materia()
