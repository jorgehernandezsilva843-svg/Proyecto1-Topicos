from repositories.alumno_repository import AlumnoRepository
from repositories.calificacion_repository import CalificacionRepository
from models.domain import Alumno

class AlumnoService:
    @staticmethod
    def insertar(alumno: Alumno) -> int:
        return AlumnoRepository.insertar(alumno)

    @staticmethod
    def listar_todos() -> list[Alumno]:
        return AlumnoRepository.listar_todos()

    @staticmethod
    def actualizar(alumno: Alumno):
        AlumnoRepository.actualizar(alumno)

    @staticmethod
    def desactivar(alumno_id: int):
        AlumnoRepository.cambiar_estado(alumno_id, 0)

    @staticmethod
    def alternar_estado(alumno_id: int):
        """
        Consulta el estado actual del alumno.
        Si está activo (1) y tiene calificaciones, lanza ValueError.
        Si está inactivo (0), lo reactiva sin restricción.
        """
        alumno = AlumnoRepository.obtener_por_id(alumno_id)
        if alumno is None:
            raise ValueError("Alumno no encontrado.")

        if int(alumno.activo) == 1:
            # Verificar integridad antes de desactivar
            if CalificacionRepository.existe_por_alumno(alumno_id):
                raise ValueError("No se puede desactivar un alumno con calificaciones registradas.")
            AlumnoRepository.cambiar_estado(alumno_id, 0)
        else:
            # Reactivar sin restricciones
            AlumnoRepository.cambiar_estado(alumno_id, 1)

    @staticmethod
    def eliminar_registro(alumno_id: int):
        if CalificacionRepository.existe_por_alumno(alumno_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        AlumnoRepository.eliminar_fisicamente(alumno_id)
