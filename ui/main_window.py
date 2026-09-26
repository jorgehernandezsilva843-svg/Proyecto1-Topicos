import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_institutional_style, PRIMARY_COLOR, WHITE_COLOR, BG_COLOR
from ui.alumnos_view import AlumnosView
from ui.materias_view import MateriasView
from ui.calificaciones_view import CalificacionesView
from ui.reportes_view import ReportesView

class MainWindow(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title("SISTEMA DE CONTROL ESCOLAR INSTITUCIONAL")
        self.geometry("1100x750")
        self.configure(bg=WHITE_COLOR)
        
        apply_institutional_style()
        self._build_ui()

    def _build_ui(self):
        # Contenedor principal que abarca toda la pantalla
        main_container = tk.Frame(self, bg=WHITE_COLOR)
        main_container.pack(fill='both', expand=True)

        # ==========================================
        # PANEL IZQUIERDO: BARRA LATERAL (SIDEBAR)
        # ==========================================
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=230)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False) # Forzar mantener el ancho de 230px

        # Encabezado del menú y bienvenida
        user_info = f"Bienvenido(a)\n{self.usuario.username}\n{self.usuario.rol.upper()}"
        ttk.Label(self.sidebar, text="MENÚ PRINCIPAL", style='Sidebar.TLabel', font=("Segoe UI", 13, "bold"), anchor='center').pack(pady=(30, 10), fill='x')
        ttk.Label(self.sidebar, text=user_info, style='Sidebar.TLabel', anchor='center', justify='center').pack(pady=(0, 40), fill='x')

        # Definición de botones apilados (Estilo menú moderno)
        botones = [
            ("ALUMNOS", lambda: self.mostrar_vista(AlumnosView)),
            ("MATERIAS", lambda: self.mostrar_vista(MateriasView)),
            ("CALIFICACIONES", lambda: self.mostrar_vista(CalificacionesView)),
            ("REPORTES", lambda: self.mostrar_vista(ReportesView)),
        ]

        for texto, comando in botones:
            btn = ttk.Button(self.sidebar, text=texto, style='Sidebar.TButton', command=comando)
            # ipady=12 da una altura cómoda para clicar (estilo flat moderno)
            btn.pack(fill='x', ipady=12, pady=1)

        # Botón de Salir (anclado al fondo de la barra)
        ttk.Frame(self.sidebar, style='Sidebar.TFrame').pack(fill='both', expand=True) # Espaciador
        ttk.Button(self.sidebar, text="CERRAR SESIÓN", style='Sidebar.TButton', command=self.cerrar_sesion).pack(fill='x', ipady=12, side='bottom', pady=(0, 20))

        # ==========================================
        # PANEL DERECHO: ÁREA DE CONTENIDO PRINCIPAL
        # ==========================================
        self.content_area = ttk.Frame(main_container, style='Content.TFrame')
        self.content_area.pack(side='right', fill='both', expand=True)
        
        self.vista_actual = None
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        """Muestra el logo o mensaje inicial al abrir el sistema."""
        self._limpiar_contenido()
        self.vista_actual = tk.Frame(self.content_area, bg=WHITE_COLOR)
        self.vista_actual.pack(fill='both', expand=True)
        
        ttk.Label(self.vista_actual, text="SISTEMA DE CONTROL ESCOLAR", style='Title.TLabel').pack(pady=(250, 20))
        ttk.Label(self.vista_actual, text="Seleccione un módulo en el menú lateral izquierdo para comenzar.", style='Content.TLabel').pack()

    def mostrar_vista(self, vista_clase):
        """Destruye la vista actual e incrusta la nueva vista dinámicamente."""
        self._limpiar_contenido()
        
        # Instanciamos la clase de la vista pasándole el área de contenido como padre
        self.vista_actual = vista_clase(self.content_area)
        
        # Si la vista hereda de Frame (como hemos configurado), la empaquetamos para que ocupe el espacio
        if hasattr(self.vista_actual, 'pack'):
            self.vista_actual.pack(fill='both', expand=True)

    def _limpiar_contenido(self):
        """Destruye el widget que esté actualmente en el área de contenido."""
        if self.vista_actual:
            self.vista_actual.destroy()

    def cerrar_sesion(self):
        self.destroy()
        # Retorno a login
        from ui.login import LoginWindow
        app = LoginWindow()
        app.mainloop()
