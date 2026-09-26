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
        """Desactiva directamente sin verificar calificaciones (compatibilidad con código existente)."""
        MateriaRepository.cambiar_estado(materia_id, 0)

    @staticmethod
    def alternar_estado(materia_id: int):
        """
        Consulta el estado actual de la materia.
        Si está activa (1) y tiene calificaciones, lanza ValueError.
        Si está inactiva (0), la reactiva sin restricción.
        """
        materia = MateriaRepository.obtener_por_id(materia_id) if hasattr(MateriaRepository, 'obtener_por_id') else None

        # Fallback: consultar desde la lista completa
        if materia is None:
            todas = MateriaRepository.listar_todos()
            materia = next((m for m in todas if m.id == materia_id), None)

        if materia is None:
            raise ValueError("Materia no encontrada.")

        if materia.activo == 1:
            if CalificacionRepository.existe_por_materia(materia_id):
                raise ValueError("No se puede desactivar una materia con calificaciones registradas.")
            MateriaRepository.cambiar_estado(materia_id, 0)
        else:
            MateriaRepository.cambiar_estado(materia_id, 1)

    @staticmethod
    def eliminar_registro(materia_id: int):
        if CalificacionRepository.existe_por_materia(materia_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        MateriaRepository.eliminar_fisicamente(materia_id)
