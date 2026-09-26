import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_institutional_style, PRIMARY_COLOR, WHITE_COLOR, BG_COLOR
from ui.alumnos_view import AlumnosView
from ui.materias_view import MateriasView
from ui.calificaciones_view import CalificacionesView
from ui.reportes_view import ReportesView

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

        # ══════════════════════════════════════
        # PANEL IZQUIERDO: BARRA LATERAL (SIDEBAR)
        # ══════════════════════════════════════
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=230)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Encabezado con nombre de usuario y rol
        user_info = f"Bienvenido(a)\n{self.usuario.username}\n{self.usuario.rol.upper()}"
        ttk.Label(self.sidebar, text="MENÚ PRINCIPAL", style='Sidebar.TLabel',
                  font=("Segoe UI", 13, "bold"), anchor='center').pack(pady=(30, 10), fill='x')
        ttk.Label(self.sidebar, text=user_info, style='Sidebar.TLabel',
                  anchor='center', justify='center').pack(pady=(0, 30), fill='x')

        # Separador visual
        tk.Frame(self.sidebar, bg="#1e4480", height=1).pack(fill='x', padx=15, pady=(0, 15))

        # Botones de módulos comunes a todos los roles
        botones_comunes = [
            ("ALUMNOS",         lambda: self.mostrar_vista(AlumnosView)),
            ("MATERIAS",        lambda: self.mostrar_vista(MateriasView)),
            ("CALIFICACIONES",  lambda: self.mostrar_vista(CalificacionesView)),
            ("REPORTES",        lambda: self.mostrar_vista(ReportesView)),
        ]
        for texto, cmd in botones_comunes:
            ttk.Button(self.sidebar, text=texto, style='Sidebar.TButton',
                       command=cmd).pack(fill='x', ipady=12, pady=1)

        # ── Botón exclusivo del Administrador ──
        # Solo visible si el usuario tiene rol 'administrador'
        es_admin = self.usuario.rol.lower() == 'administrador'
        self.btn_usuarios = ttk.Button(
            self.sidebar,
            text="GESTIÓN DE USUARIOS",
            style='Sidebar.TButton',
            command=self.abrir_gestion_usuarios,
            state='normal' if es_admin else 'disabled'
        )
        self.btn_usuarios.pack(fill='x', ipady=12, pady=1)

        if not es_admin:
            # Ocultarlo completamente para el operador (más limpio que dejarlo gris)
            self.btn_usuarios.pack_forget()

        # Espaciador + Cerrar Sesión al fondo
        ttk.Frame(self.sidebar, style='Sidebar.TFrame').pack(fill='both', expand=True)
        ttk.Button(self.sidebar, text="CERRAR SESIÓN", style='Sidebar.TButton',
                   command=self.cerrar_sesion).pack(fill='x', ipady=12, side='bottom', pady=(0, 20))

        # ══════════════════════════════════════
        # PANEL DERECHO: ÁREA DE CONTENIDO
        # ══════════════════════════════════════
        self.content_area = ttk.Frame(main_container, style='Content.TFrame')
        self.content_area.pack(side='right', fill='both', expand=True)

        self.vista_actual = None
        self.mostrar_bienvenida()

    # ── Pantalla de bienvenida ────────────────────────────────────────────────

    def mostrar_bienvenida(self):
        self._limpiar_contenido()
        self.vista_actual = tk.Frame(self.content_area, bg=WHITE_COLOR)
        self.vista_actual.pack(fill='both', expand=True)

        self._logo_bienvenida = None
        try:
            from PIL import Image, ImageTk
            img = Image.open(_LOGO_PATH).convert("RGBA")
            r, g, b, a = img.split()
            a = a.point(lambda p: int(p * 0.18))
            img.putalpha(a)
            img = img.resize((420, 420), Image.LANCZOS)
            self._logo_bienvenida = ImageTk.PhotoImage(img)
        except ImportError:
            try:
                self._logo_bienvenida = tk.PhotoImage(file=_LOGO_PATH)
            except Exception:
                pass
        except Exception:
            pass

        if self._logo_bienvenida:
            lbl_img = tk.Label(self.vista_actual, image=self._logo_bienvenida,
                               bg=WHITE_COLOR, bd=0)
            lbl_img.place(relx=0.5, rely=0.5, anchor='center')
            lbl_img.lower()

        ttk.Label(self.vista_actual, text="SISTEMA DE CONTROL ESCOLAR",
                  style='Title.TLabel').pack(pady=(220, 15))
        ttk.Label(self.vista_actual,
                  text="Seleccione un módulo en el menú lateral izquierdo para comenzar.",
                  style='Content.TLabel').pack()

    # ── Navegación dinámica ───────────────────────────────────────────────────

    def mostrar_vista(self, vista_clase):
        self._limpiar_contenido()
        self.vista_actual = vista_clase(self.content_area)
        if hasattr(self.vista_actual, 'pack'):
            self.vista_actual.pack(fill='both', expand=True)

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
