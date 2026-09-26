import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ui.styles import WHITE_COLOR
from repositories.calificacion_repository import CalificacionRepository
from services.calificacion_service import CalificacionService

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

class ReportesView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        self.generar_reporte()
        if MATPLOTLIB_AVAILABLE:
            self.generar_grafica()

    def _poner_fondo(self):
        try:
            from PIL import Image, ImageTk
            img = Image.open(_LOGO_PATH).convert("RGBA")
            r, g, b, a = img.split()
            a = a.point(lambda p: int(p * 0.12))
            img.putalpha(a)
            img = img.resize((340, 340), Image.LANCZOS)
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
        ttk.Label(self, text="BOLETA DE ALUMNOS REPROBADOS (< 70) Y ESTADÍSTICAS", style='Title.TLabel').pack(pady=(10, 20))

        content_frame = tk.Frame(self, bg=WHITE_COLOR)
        content_frame.pack(fill='both', expand=True, padx=20, pady=5)

        # Left side: Treeview + Buttons
        left_frame = tk.Frame(content_frame, bg=WHITE_COLOR)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        tree_frame = tk.Frame(left_frame, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True)

        columnas = ("Alumno", "Materia Reprobada", "Nota", "Promedio General")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)

        anchos = {"Alumno": 150, "Materia Reprobada": 150, "Nota": 80, "Promedio General": 110}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 100), anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        btn_frame = tk.Frame(left_frame, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', pady=10)

        ttk.Button(btn_frame, text="↻ Actualizar Reporte", command=self.actualizar_todo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exportar a CSV", command=self.exportar_csv).pack(side='left', padx=5)

        # Right side: Graph
        self.graph_frame = tk.Frame(content_frame, bg=WHITE_COLOR, width=400)
        self.graph_frame.pack(side='right', fill='both', expand=True)

    def actualizar_todo(self):
        self.generar_reporte()
        if MATPLOTLIB_AVAILABLE:
            self.generar_grafica()

    def generar_reporte(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            calificaciones = CalificacionRepository.obtener_calificaciones_join()
            datos_promedio = {}
            for c in calificaciones:
                nombre = c['nombre_alumno']
                nota   = float(c['nota'])
                if nombre not in datos_promedio:
                    datos_promedio[nombre] = {'suma': 0.0, 'conteo': 0}
                datos_promedio[nombre]['suma']   += nota
                datos_promedio[nombre]['conteo'] += 1

            for c in calificaciones:
                nota = float(c['nota'])
                if nota < 70.0:
                    nombre   = c['nombre_alumno']
                    materia  = c['nombre_materia']
                    promedio = datos_promedio[nombre]['suma'] / datos_promedio[nombre]['conteo']
                    self.tree.insert("", "end", values=(nombre, materia, f"{nota:.2f}", f"{promedio:.2f}"))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def exportar_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Exportar a CSV"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Escribir encabezados
                columnas = [self.tree.heading(col, 'text') for col in self.tree['columns']]
                writer.writerow(columnas)
                
                # Escribir datos
                for row_id in self.tree.get_children():
                    row = self.tree.item(row_id)['values']
                    writer.writerow(row)
                    
            messagebox.showinfo("ÉXITO", "Los datos se exportaron correctamente a CSV.")
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar el archivo CSV:\n{e}")

    def generar_grafica(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        try:
            datos = CalificacionService.obtener_promedio_por_materia()
            if not datos:
                ttk.Label(self.graph_frame, text="No hay datos suficientes para graficar.", style='Content.TLabel').pack(pady=50)
                return

            materias = [d[0] for d in datos]
            promedios = [d[1] for d in datos]

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(materias, promedios, color='#132c54')
            ax.set_ylim([0, 100])
            ax.set_ylabel('Promedio')
            ax.set_title('Promedio por Materia')
            
            # Rotate x labels if there are many subjects or long names
            fig.autofmt_xdate(rotation=45)

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            ttk.Label(self.graph_frame, text="Error al generar gráfica.", style='Content.TLabel').pack(pady=50)
            print(f"Error gráfica: {e}")
