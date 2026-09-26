import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from services.alumno_service import AlumnoService
from services.materia_service import MateriaService
from services.calificacion_service import CalificacionService
from repositories.calificacion_repository import CalificacionRepository

class CalificacionesView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self.mapa_alumnos = {}
        self.mapa_materias = {}
        self._build_ui()
        self.cargar_datos_iniciales()
        self.cargar_calificaciones()

    def _build_ui(self):
        ttk.Label(self, text="REGISTRO DE CALIFICACIONES", style='Title.TLabel').pack(pady=(10, 20))

        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(form_frame, text="Alumno:", style='Content.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.combo_alumnos = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_alumnos.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Materia:", style='Content.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.combo_materias = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_materias.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Periodo (Ej. 2023-1):", style='Content.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.periodo_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.periodo_var, width=20).grid(row=2, column=1, sticky='w', padx=10, pady=5)

        ttk.Label(form_frame, text="Nota (0-100):", style='Content.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        self.nota_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nota_var, width=10).grid(row=3, column=1, sticky='w', padx=10, pady=5)

        ttk.Button(form_frame, text="Registrar Nota", command=self.registrar).grid(row=4, column=0, columnspan=2, pady=15)

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("ID", "Alumno", "Materia", "Periodo", "Nota")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def cargar_datos_iniciales(self):
        try:
            alumnos = AlumnoService.listar_todos()
            materias = MateriaService.listar_todos()
            self.mapa_alumnos = {f"{a.matricula} - {a.nombre}": a.id for a in alumnos}
            self.mapa_materias = {f"{m.clave} - {m.nombre}": m.id for m in materias}
            self.combo_alumnos['values'] = list(self.mapa_alumnos.keys())
            self.combo_materias['values'] = list(self.mapa_materias.keys())
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def cargar_calificaciones(self):
        for fila in self.tree.get_children():
            self.tree.delete(fila)
        try:
            calificaciones = CalificacionRepository.obtener_calificaciones_join()
            for c in calificaciones:
                self.tree.insert("", "end", values=(c['id_calificacion'], c['nombre_alumno'], c['nombre_materia'], c['periodo'], c['nota']))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def registrar(self):
        seleccion_alumno = self.combo_alumnos.get()
        seleccion_materia = self.combo_materias.get()
        periodo = self.periodo_var.get().strip()
        nota_str = self.nota_var.get().strip()

        if not all([seleccion_alumno, seleccion_materia, periodo, nota_str]):
            messagebox.showwarning("ERROR", "Todos los campos son requeridos.")
            return

        try:
            nota = float(nota_str)
            alumno_id = self.mapa_alumnos[seleccion_alumno]
            materia_id = self.mapa_materias[seleccion_materia]
            CalificacionService.registrar_calificacion(alumno_id, materia_id, periodo, nota)
            
            messagebox.showinfo("ÉXITO", "Calificación registrada.")
            self.periodo_var.set("")
            self.nota_var.set("")
            self.cargar_calificaciones()
        except ValueError as ve:
            messagebox.showerror("REGLA DE NEGOCIO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))
