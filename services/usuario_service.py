import hashlib
from db.database import get_connection
from models.domain import Usuario

class UsuarioService:
    @staticmethod
    def autenticar(username: str, password: str) -> Usuario | None:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        cursor.execute('SELECT id, username, rol, activo FROM usuarios_sistema WHERE username = ? AND password_hash = ?', (username, password_hash))
        fila = cursor.fetchone()
        conn.close()
        
        if fila:
            return Usuario(id=fila[0], username=fila[1], rol=fila[2], activo=fila[3])
        return None
