import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_institutional_style, PRIMARY_COLOR, WHITE_COLOR, BG_COLOR
from ui.alumnos_view import AlumnosView
from ui.materias_view import MateriasView
from ui.calificaciones_view import CalificacionesView
from ui.reportes_view import ReportesView
from ui.graficas_view import GraficasView
from ui.bitacora_view import BitacoraView
from ui.dashboard_view import DashboardView

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

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
        main_container = tk.Frame(self, bg=WHITE_COLOR)
        main_container.pack(fill='both', expand=True)

        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=230)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        user_info = f"Bienvenido(a)\n{self.usuario.username}\n{self.usuario.rol.upper()}"
        ttk.Label(self.sidebar, text="MENÚ PRINCIPAL", style='Sidebar.TLabel',
                  font=("Segoe UI", 13, "bold"), anchor='center').pack(pady=(30, 10), fill='x')
        ttk.Label(self.sidebar, text=user_info, style='Sidebar.TLabel',
                  anchor='center', justify='center').pack(pady=(0, 30), fill='x')

        tk.Frame(self.sidebar, bg="#1e4480", height=1).pack(fill='x', padx=15, pady=(0, 15))

        botones_comunes = [
            ("ALUMNOS",         lambda: self.mostrar_vista(AlumnosView)),
            ("MATERIAS",        lambda: self.mostrar_vista(MateriasView)),
            ("CALIFICACIONES",  lambda: self.mostrar_vista(CalificacionesView)),
            ("REPORTES",        lambda: self.mostrar_vista(ReportesView)),
            ("GRÁFICAS",        lambda: self.mostrar_vista(GraficasView)),
        ]
        for texto, cmd in botones_comunes:
            ttk.Button(self.sidebar, text=texto, style='Sidebar.TButton',
                       command=cmd).pack(fill='x', ipady=5, pady=1)

        es_admin = self.usuario.rol.lower() == 'administrador'
        
        self.btn_usuarios = ttk.Button(
            self.sidebar,
            text="GESTIÓN DE USUARIOS",
            style='Sidebar.TButton',
            command=self.abrir_gestion_usuarios,
            state='normal' if es_admin else 'disabled'
        )
        self.btn_usuarios.pack(fill='x', ipady=5, pady=1)

        self.btn_bitacora = ttk.Button(
            self.sidebar,
            text="BITÁCORA DE ACCIONES",
            style='Sidebar.TButton',
            command=lambda: self.mostrar_vista(BitacoraView),
            state='normal' if es_admin else 'disabled'
        )
        self.btn_bitacora.pack(fill='x', ipady=5, pady=1)

        if not es_admin:
            self.btn_usuarios.pack_forget()
            self.btn_bitacora.pack_forget()

        # Tema toggle button
        self.modo_actual = 'claro'
        self.btn_tema = ttk.Button(
            self.sidebar,
            text="🌙 Modo Oscuro",
            style='Sidebar.TButton',
            command=self.alternar_tema
        )
        self.btn_tema.pack(fill='x', ipady=5, pady=1)

        # Espaciador + Logo TecNM + Cerrar Sesión al fondo
        ttk.Frame(self.sidebar, style='Sidebar.TFrame').pack(fill='both', expand=True)

        self._logo_sidebar = None
        try:
            from PIL import Image, ImageTk
            img = Image.open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")).convert("RGBA")
            # Agrandar el logo al ancho completo del sidebar (230px), manteniendo proporción
            proporcional_h = int(img.height * (230 / img.width))
            img = img.resize((230, proporcional_h), Image.LANCZOS)
            self._logo_sidebar = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(self.sidebar, image=self._logo_sidebar, bg="#132c54", bd=0)
            lbl_logo.pack(pady=0)
        except Exception:
            pass

        ttk.Button(self.sidebar, text="CERRAR SESIÓN", style='Sidebar.TButton',
                   command=self.cerrar_sesion).pack(fill='x', ipady=5, side='bottom', pady=(0, 0))

        # ══════════════════════════════════════
        # PANEL DERECHO: ÁREA DE CONTENIDO
        # ══════════════════════════════════════
        self.content_area = ttk.Frame(main_container, style='Content.TFrame')
        self.content_area.pack(side='right', fill='both', expand=True)

        self.vista_actual = None
        # Cargar Dashboard por defecto
        self.mostrar_vista(DashboardView)

    def alternar_tema(self):
        from ui.styles import aplicar_tema
        if self.modo_actual == 'claro':
            self.modo_actual = 'oscuro'
            self.btn_tema.config(text="☀️ Modo Claro")
        else:
            self.modo_actual = 'claro'
            self.btn_tema.config(text="🌙 Modo Oscuro")
        
        aplicar_tema(self.modo_actual, self)

        # Matplotlib theme support if the current view is DashboardView or GraficasView
        if hasattr(self.vista_actual, 'generar_grafica'):
            self.vista_actual.generar_grafica()

    # ── Navegación dinámica ───────────────────────────────────────────────────

    def mostrar_vista(self, vista_clase):
        self._limpiar_contenido()
        self.vista_actual = vista_clase(self.content_area, usuario=self.usuario)
        if hasattr(self.vista_actual, 'pack'):
            self.vista_actual.pack(fill='both', expand=True)
            
        # Re-aplicar el tema a la nueva vista cargada
        from ui.styles import aplicar_tema
        aplicar_tema(self.modo_actual, self)

    def _limpiar_contenido(self):
        if self.vista_actual:
            self.vista_actual.destroy()

    # ── Módulo exclusivo del Administrador ───────────────────────────────────

    def abrir_gestion_usuarios(self):
        """Abre el módulo de gestión de usuarios (solo administrador)."""
        messagebox.showinfo(
            "GESTIÓN DE USUARIOS",
            "Módulo de Gestión de Personal.\n\n"
            "Usuarios registrados en el sistema:\n"
            "  • admin (administrador)\n"
            "  • maestro (operador)\n\n"
            "Para agregar más usuarios, contacte al administrador del sistema."
        )

    # ── Cerrar sesión ─────────────────────────────────────────────────────────

    def cerrar_sesion(self):
        self.destroy()
        from ui.login import LoginWindow
        app = LoginWindow()
        app.mainloop()
