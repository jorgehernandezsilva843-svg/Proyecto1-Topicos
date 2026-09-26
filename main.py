import sys
from db.database import inicializar_db
from ui.login import LoginWindow

def main():
    print("[SISTEMA] Inicializando motor de base de datos...")
    try:
        inicializar_db()
        print("[SISTEMA] Base de datos en línea. Llaves foráneas activas.")
    except Exception as e:
        print(f"[FATAL ERROR] Fallo al inicializar la base de datos: {e}")
        sys.exit(1)
        
    print("[SISTEMA] Arrancando interfaz gráfica (UI)...")
    app_login = LoginWindow()
    app_login.mainloop()
    print("[SISTEMA] Secuencia de apagado completada.")

if __name__ == "__main__":
    main()
