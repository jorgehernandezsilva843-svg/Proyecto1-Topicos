from db.database import get_connection

class DashboardRepository:
    @staticmethod
    def obtener_estadisticas():
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM alumnos")
            total_alumnos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM materias")
            total_materias = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(nota) FROM calificaciones")
            promedio_res = cursor.fetchone()[0]
            promedio = round(promedio_res, 2) if promedio_res else 0.0
            
            return total_alumnos, total_materias, promedio
        finally:
            conn.close()
