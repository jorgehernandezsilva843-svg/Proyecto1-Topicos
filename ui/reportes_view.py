import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from repositories.calificacion_repository import CalificacionRepository

class ReportesView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self._build_ui()
        self.generar_reporte()

    def _build_ui(self):
        ttk.Label(self, text="BOLETA DE ALUMNOS REPROBADOS (< 70)", style='Title.TLabel').pack(pady=(10, 20))

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("Alumno", "Materia Reprobada", "Nota", "Promedio General")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings")
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def generar_reporte(self):
        try:
            calificaciones = CalificacionRepository.obtener_calificaciones_join()
            datos_promedio = {}
            for c in calificaciones:
                nombre = c['nombre_alumno']
                nota = float(c['nota'])
                if nombre not in datos_promedio:
                    datos_promedio[nombre] = {'suma': 0.0, 'conteo': 0}
                datos_promedio[nombre]['suma'] += nota
                datos_promedio[nombre]['conteo'] += 1

            for c in calificaciones:
                nota = float(c['nota'])
                if nota < 70.0:
                    nombre = c['nombre_alumno']
                    materia = c['nombre_materia']
                    promedio_general = datos_promedio[nombre]['suma'] / datos_promedio[nombre]['conteo']
                    self.tree.insert("", "end", values=(nombre, materia, f"{nota:.2f}", f"{promedio_general:.2f}"))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))
