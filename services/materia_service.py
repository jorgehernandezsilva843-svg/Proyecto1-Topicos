from repositories.materia_repository import MateriaRepository
from repositories.calificacion_repository import CalificacionRepository
from models.domain import Materia

class MateriaService:
    @staticmethod
    def insertar(materia: Materia) -> int:
        return MateriaRepository.insertar(materia)
        
    @staticmethod
    def listar_todos() -> list[Materia]:
        return MateriaRepository.listar_todos()

    @staticmethod
    def actualizar(materia: Materia):
        MateriaRepository.actualizar(materia)

    @staticmethod
    def desactivar(materia_id: int):
        if CalificacionRepository.existe_por_materia(materia_id):
            raise ValueError("No se puede desactivar un registro con movimientos activos.")
        MateriaRepository.desactivar(materia_id)

    @staticmethod
    def eliminar_registro(materia_id: int):
        if CalificacionRepository.existe_por_materia(materia_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        MateriaRepository.eliminar_fisicamente(materia_id)
