import os

BASE_DIR = r"C:\Users\Administrador\Desktop\Fund. & Simulación\Proyecto1 Topicos"

def write_file(path, content):
    with open(os.path.join(BASE_DIR, path), 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

# 1. ui/login.py
write_file(r"ui\login.py", r"""
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
""")

# 2. ui/alumnos_view.py
write_file(r"ui\alumnos_view.py", r"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from models.domain import Alumno
from services.alumno_service import AlumnoService

class AlumnosView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self.alumno_id_actual = None
        self.alumnos_en_memoria = []
        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        ttk.Label(self, text="GESTIÓN DE ALUMNOS", style='Title.TLabel').pack(pady=(10, 20))

        search_frame = tk.Frame(self, bg=WHITE_COLOR)
        search_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(search_frame, text="Buscar (Nombre/Matrícula):", style='Content.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="Mostrar Todos", command=self.cargar_datos).pack(side='left', padx=5)

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("ID", "Matrícula", "Nombre", "Correo", "Grupo", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=10)

        self.matricula_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.correo_var = tk.StringVar()
        self.grupo_var = tk.StringVar()

        campos = [
            ("Matrícula:", self.matricula_var),
            ("Nombre:", self.nombre_var),
            ("Correo:", self.correo_var),
            ("Grupo:", self.grupo_var)
        ]

        for i, (label_text, var) in enumerate(campos):
            ttk.Label(form_frame, text=label_text, style='Content.TLabel').grid(row=i, column=0, sticky='w', pady=5)
            ttk.Entry(form_frame, textvariable=var, width=50).grid(row=i, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(10, 20))

        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Desactivar", command=self.desactivar).pack(side='right', padx=5)

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.alumnos_en_memoria = AlumnoService.listar_todos()
            self._actualizar_treeview(self.alumnos_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", f"Fallo al cargar datos:\n{e}")

    def _actualizar_treeview(self, lista_alumnos):
        for fila in self.tree.get_children():
            self.tree.delete(fila)
        for a in lista_alumnos:
            estado = "ACTIVO" if str(a.activo) in ['1', 'activo', 'True'] else "INACTIVO"
            self.tree.insert("", "end", values=(a.id, a.matricula, a.nombre, a.correo, a.grupo, estado))

    def filtrar(self):
        termino = self.search_var.get().strip().lower()
        if not termino:
            return
        filtrados = [a for a in self.alumnos_en_memoria if termino in a.nombre.lower() or termino in a.matricula.lower()]
        self._actualizar_treeview(filtrados)

    def seleccionar_registro(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        valores = self.tree.item(seleccion[0], 'values')
        self.alumno_id_actual = int(valores[0])
        self.matricula_var.set(valores[1])
        self.nombre_var.set(valores[2])
        self.correo_var.set(valores[3])
        self.grupo_var.set(valores[4])

    def guardar(self):
        matricula = self.matricula_var.get().strip()
        nombre = self.nombre_var.get().strip()
        correo = self.correo_var.get().strip()
        grupo = self.grupo_var.get().strip()

        if not all([matricula, nombre, correo, grupo]):
            messagebox.showwarning("ADVERTENCIA", "Todos los campos son obligatorios.")
            return

        alumno = Alumno(id=self.alumno_id_actual, matricula=matricula, nombre=nombre, correo=correo, grupo=grupo)

        try:
            if self.alumno_id_actual is None:
                AlumnoService.insertar(alumno)
                messagebox.showinfo("ÉXITO", "Alumno registrado.")
            else:
                AlumnoService.actualizar(alumno)
                messagebox.showinfo("ÉXITO", "Alumno actualizado.")
                
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR DE SISTEMA", f"No se pudo guardar:\n{str(e)}")

    def desactivar(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione un alumno primero.")
            return
        respuesta = messagebox.askyesno("CONFIRMAR", "¿Seguro que desea desactivar al alumno?")
        if not respuesta:
            return
        try:
            AlumnoService.desactivar(self.alumno_id_actual)
            messagebox.showinfo("ÉXITO", "Alumno desactivado.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def limpiar_formulario(self):
        self.alumno_id_actual = None
        self.matricula_var.set("")
        self.nombre_var.set("")
        self.correo_var.set("")
        self.grupo_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
""")

# 3. ui/materias_view.py
write_file(r"ui\materias_view.py", r"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from models.domain import Materia
from services.materia_service import MateriaService

class MateriasView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self.materia_id_actual = None
        self.materias_en_memoria = []
        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        ttk.Label(self, text="GESTIÓN DE MATERIAS", style='Title.TLabel').pack(pady=(10, 20))

        search_frame = tk.Frame(self, bg=WHITE_COLOR)
        search_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(search_frame, text="Buscar (Nombre/Clave):", style='Content.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="Mostrar Todas", command=self.cargar_datos).pack(side='left', padx=5)

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("ID", "Clave", "Nombre", "Créditos", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=8)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=10)

        self.clave_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.creditos_var = tk.StringVar()

        campos = [
            ("Clave:", self.clave_var),
            ("Nombre:", self.nombre_var),
            ("Créditos:", self.creditos_var)
        ]

        for i, (label_text, var) in enumerate(campos):
            ttk.Label(form_frame, text=label_text, style='Content.TLabel').grid(row=i, column=0, sticky='w', pady=5)
            ttk.Entry(form_frame, textvariable=var, width=40).grid(row=i, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(10, 20))

        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Desactivar", command=self.desactivar).pack(side='right', padx=5)

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.materias_en_memoria = MateriaService.listar_todos()
            self._actualizar_treeview(self.materias_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", f"Fallo al cargar datos:\n{e}")

    def _actualizar_treeview(self, lista_materias):
        for fila in self.tree.get_children():
            self.tree.delete(fila)
        for m in lista_materias:
            estado = "ACTIVA" if str(m.activo) in ['1', 'activo', 'True'] else "INACTIVA"
            self.tree.insert("", "end", values=(m.id, m.clave, m.nombre, m.creditos, estado))

    def filtrar(self):
        termino = self.search_var.get().strip().lower()
        if not termino:
            return
        filtradas = [m for m in self.materias_en_memoria if termino in m.nombre.lower() or termino in m.clave.lower()]
        self._actualizar_treeview(filtradas)

    def seleccionar_registro(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        valores = self.tree.item(seleccion[0], 'values')
        self.materia_id_actual = int(valores[0])
        self.clave_var.set(valores[1])
        self.nombre_var.set(valores[2])
        self.creditos_var.set(valores[3])

    def guardar(self):
        clave = self.clave_var.get().strip()
        nombre = self.nombre_var.get().strip()
        creditos_str = self.creditos_var.get().strip()

        if not all([clave, nombre, creditos_str]):
            messagebox.showwarning("ADVERTENCIA", "Todos los campos son obligatorios.")
            return
        if not creditos_str.isdigit():
            messagebox.showwarning("ERROR", "Los créditos deben ser numéricos.")
            return

        materia = Materia(id=self.materia_id_actual, clave=clave, nombre=nombre, creditos=int(creditos_str))

        try:
            if self.materia_id_actual is None:
                MateriaService.insertar(materia)
                messagebox.showinfo("ÉXITO", "Materia registrada.")
            else:
                MateriaService.actualizar(materia)
                messagebox.showinfo("ÉXITO", "Materia actualizada.")
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo guardar:\n{str(e)}")

    def desactivar(self):
        if self.materia_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione una materia primero.")
            return
        respuesta = messagebox.askyesno("CONFIRMAR", "¿Seguro que desea desactivar la materia?")
        if not respuesta:
            return
        try:
            MateriaService.desactivar(self.materia_id_actual)
            messagebox.showinfo("ÉXITO", "Materia desactivada.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def limpiar_formulario(self):
        self.materia_id_actual = None
        self.clave_var.set("")
        self.nombre_var.set("")
        self.creditos_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
""")

# 4. ui/calificaciones_view.py
write_file(r"ui\calificaciones_view.py", r"""
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
""")

# 5. ui/reportes_view.py
write_file(r"ui\reportes_view.py", r"""
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
""")
