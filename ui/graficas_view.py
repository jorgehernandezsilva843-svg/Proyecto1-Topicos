import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from services.calificacion_service import CalificacionService

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")


class GraficasView(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master, bg=WHITE_COLOR)
        self.usuario = usuario
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        if MATPLOTLIB_AVAILABLE:
            self.generar_grafica()
        else:
            ttk.Label(self.graph_frame, text="Matplotlib no está instalado. Ejecute:\n\npy -m pip install matplotlib", 
                      style='Content.TLabel', justify='center').pack(pady=50)

    def _poner_fondo(self):
        try:
            from PIL import Image, ImageTk
            img = Image.open(_LOGO_PATH).convert("RGBA")
            img = img.resize((340, 150), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
        except ImportError:
            try:
                self._logo_img = tk.PhotoImage(file=_LOGO_PATH)
            except Exception:
                return
        except Exception:
            return
        lbl = tk.Label(self, image=self._logo_img, bg=WHITE_COLOR, bd=0)
        lbl.place(relx=0.5, rely=0.55, anchor='center')
        lbl.lower()

    def _build_ui(self):
        ttk.Label(self, text="ANÁLISIS ESTADÍSTICO - PROMEDIOS", style='Title.TLabel').pack(pady=(10, 20))
        
        ttk.Button(self, text="↻ Actualizar Gráfica", command=self.generar_grafica).pack(pady=(0, 10))

        self.graph_frame = tk.Frame(self, bg=WHITE_COLOR)
        self.graph_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def generar_grafica(self):
        if not MATPLOTLIB_AVAILABLE: return
        
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        try:
            datos = CalificacionService.obtener_promedio_por_materia()
            if not datos:
                ttk.Label(self.graph_frame, text="No hay calificaciones suficientes para graficar.", style='Content.TLabel').pack(pady=50)
                return

            materias = [d[0] for d in datos]
            promedios = [d[1] for d in datos]

            # Hardcoded list of distinct colors to avoid numpy / colormap deprecation issues
            colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            # Replicate colors if there are more matters than colors
            colores_barras = [colores[i % len(colores)] for i in range(len(materias))]

            fig = plt.Figure(figsize=(8, 5), dpi=100)
            ax = fig.add_subplot(111)
            
            bars = ax.bar(materias, promedios, color=colores_barras)
            ax.set_ylim([0, 100])
            ax.set_ylabel('Promedio General')
            ax.set_title('Promedio Histórico por Materia')
            
            # Rotate labels so they are readable
            fig.autofmt_xdate(rotation=35)
            # Add bottom margin so rotated labels are not cut off
            fig.subplots_adjust(bottom=0.3)

            # Opcional: Agregar el número encima de la barra
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}", ha='center', va='bottom', fontsize=9)

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            ttk.Label(self.graph_frame, text=f"Error al generar gráfica:\n{str(e)}", style='Content.TLabel').pack(pady=50)
            print(f"Error gráfica: {e}")
