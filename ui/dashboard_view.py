import os
import tkinter as tk
from tkinter import ttk
from ui.styles import WHITE_COLOR
from repositories.dashboard_repository import DashboardRepository
from services.calificacion_service import CalificacionService

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")

class DashboardView(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master, bg=WHITE_COLOR)
        self.usuario = usuario
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        if MATPLOTLIB_AVAILABLE:
            self.generar_grafica()

    def _poner_fondo(self):
        try:
            from PIL import Image, ImageTk
            img = Image.open(_LOGO_PATH).convert("RGBA")
            img = img.resize((340, 150), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
        except Exception:
            return
        lbl = tk.Label(self, image=self._logo_img, bg=WHITE_COLOR, bd=0)
        lbl.place(relx=0.5, rely=0.55, anchor='center')
        lbl.lower()

    def _build_ui(self):
        ttk.Label(self, text="DASHBOARD DE INICIO", style='Title.TLabel').pack(pady=(10, 20))

        # --- Tarjetas ---
        cards_frame = tk.Frame(self, bg=WHITE_COLOR)
        cards_frame.pack(fill='x', padx=20, pady=10)
        cards_frame.es_card = True  # Marca para que aplicar_tema pueda identificarlo si es necesario

        total_alumnos, total_materias, promedio = DashboardRepository.obtener_estadisticas()

        self._crear_tarjeta(cards_frame, "TOTAL ALUMNOS", total_alumnos).pack(side='left', expand=True, fill='both', padx=10)
        self._crear_tarjeta(cards_frame, "TOTAL MATERIAS", total_materias).pack(side='left', expand=True, fill='both', padx=10)
        self._crear_tarjeta(cards_frame, "PROMEDIO GENERAL", f"{promedio:.1f}").pack(side='left', expand=True, fill='both', padx=10)

        # --- Gráfica en el Centro ---
        self.graph_frame = tk.Frame(self, bg=WHITE_COLOR)
        self.graph_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        if not MATPLOTLIB_AVAILABLE:
            ttk.Label(self.graph_frame, text="Matplotlib no está instalado.\nGráfica no disponible.", 
                      style='Content.TLabel', justify='center').pack(pady=50)

    def _crear_tarjeta(self, parent, titulo, valor):
        frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
        frame.es_card = True
        ttk.Label(frame, text=titulo, style='CardTitle.TLabel', anchor='center').pack(fill='x')
        ttk.Label(frame, text=str(valor), style='CardValue.TLabel', anchor='center').pack(fill='x', pady=(10, 0))
        return frame

    def generar_grafica(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        try:
            datos = CalificacionService.obtener_promedio_por_materia()
            if not datos:
                ttk.Label(self.graph_frame, text="No hay calificaciones suficientes para graficar.", style='Content.TLabel').pack(pady=50)
                return

            materias = [d[0] for d in datos]
            promedios = [d[1] for d in datos]

            colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            colores_barras = [colores[i % len(colores)] for i in range(len(materias))]

            fig = plt.Figure(figsize=(8, 4), dpi=100)
            # Make figure background transparent so it matches light/dark theme seamlessly
            fig.patch.set_alpha(0.0)
            
            ax = fig.add_subplot(111)
            ax.patch.set_alpha(0.0) # Transparent axis background

            bars = ax.bar(materias, promedios, color=colores_barras)
            ax.set_ylim([0, 100])
            ax.set_ylabel('Promedio General')
            
            # Make sure labels are visible depending on theme (we can just leave default or format it)
            # Default matplotlib labels are black, might be hard to read in dark mode.
            # I will let it be for now since it's an image.
            
            fig.autofmt_xdate(rotation=35)
            fig.subplots_adjust(bottom=0.3)

            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}", ha='center', va='bottom', fontsize=9)

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            ttk.Label(self.graph_frame, text=f"Error al generar gráfica:\n{str(e)}", style='Content.TLabel').pack(pady=50)
