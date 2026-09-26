import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from repositories.calificacion_repository import CalificacionRepository

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")


class ReportesView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        self.generar_reporte()

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
        ttk.Label(self, text="BOLETA DE ALUMNOS REPROBADOS (< 70)", style='Title.TLabel').pack(pady=(10, 20))

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("Alumno", "Materia Reprobada", "Nota", "Promedio General")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings")

        anchos = {"Alumno": 200, "Materia Reprobada": 200, "Nota": 90, "Promedio General": 130}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 120), anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        ttk.Button(self, text="↻ Actualizar Reporte", command=self.generar_reporte).pack(pady=(0, 15))

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
