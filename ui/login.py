import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_institutional_style, WHITE_COLOR, BG_COLOR
from ui.main_window import MainWindow
from services.usuario_service import UsuarioService

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SISTEMA DE CONTROL ESCOLAR - LOGIN")
        self.geometry("450x350")
        self.configure(bg=WHITE_COLOR)
        self.resizable(False, False)
        
        apply_institutional_style()
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, style='Content.TFrame', padding=30)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="INICIAR SESIÓN", style='Title.TLabel').pack(pady=(0, 30))

        ttk.Label(frame, text="USUARIO:", style='Content.TLabel').pack(anchor='w')
        self.entry_user = ttk.Entry(frame)
        self.entry_user.pack(fill='x', pady=(0, 15), ipady=5)

        ttk.Label(frame, text="CONTRASEÑA:", style='Content.TLabel').pack(anchor='w')
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.pack(fill='x', pady=(0, 30), ipady=5)

        ttk.Button(frame, text="ENTRAR", command=self.intentar_login).pack(fill='x', ipady=5)

    def intentar_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("CAMPOS INCOMPLETOS", "LOS CAMPOS NO PUEDEN ESTAR VACÍOS.")
            return

        try:
            usuario = UsuarioService.autenticar(username, password)
            
            if not usuario:
                messagebox.showerror("ACCESO DENEGADO", "CREDENCIALES INCORRECTAS.")
                return
                
            if str(usuario.activo).lower() in ['0', 'inactivo', 'false']:
                messagebox.showerror("ACCESO DENEGADO", "CUENTA DE USUARIO DESACTIVADA.")
                return
            
            self.destroy()
            app = MainWindow(usuario)
            app.mainloop()
            
        except Exception as e:
            messagebox.showerror("ERROR DEL SISTEMA", str(e))
