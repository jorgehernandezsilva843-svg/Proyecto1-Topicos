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
        if CalificacionRepository.existe_por_alumno(alumno_id):
            raise ValueError("No se puede desactivar un registro con movimientos activos.")
        AlumnoRepository.desactivar(alumno_id)

    @staticmethod
    def eliminar_registro(alumno_id: int):
        if CalificacionRepository.existe_por_alumno(alumno_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        AlumnoRepository.eliminar_fisicamente(alumno_id)
