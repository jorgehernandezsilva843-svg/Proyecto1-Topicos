import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from services.alumno_service import AlumnoService
from services.materia_service import MateriaService
from services.calificacion_service import CalificacionService
from repositories.calificacion_repository import CalificacionRepository

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")


class CalificacionesView(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master, bg=WHITE_COLOR)
        self.usuario = usuario
        self.calificacion_id_actual = None   # ID de la calificación seleccionada (para UPDATE)
        self.mapa_alumnos  = {}
        self.mapa_materias = {}
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        self.cargar_datos_iniciales()
        self.cargar_calificaciones()

    # ── Fondo ────────────────────────────────────────────────────────────────

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
        lbl.place(relx=0.5, rely=0.62, anchor='center')
        lbl.lower()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        ttk.Label(self, text="REGISTRO DE CALIFICACIONES", style='Title.TLabel').pack(pady=(10, 15))

        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=8)

        ttk.Label(form_frame, text="Alumno:", style='Content.TLabel').grid(row=0, column=0, sticky='w', pady=4)
        self.combo_alumnos = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_alumnos.grid(row=0, column=1, padx=10, pady=4)

        ttk.Label(form_frame, text="Materia:", style='Content.TLabel').grid(row=1, column=0, sticky='w', pady=4)
        self.combo_materias = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_materias.grid(row=1, column=1, padx=10, pady=4)

        ttk.Label(form_frame, text="Periodo:", style='Content.TLabel').grid(row=2, column=0, sticky='w', pady=4)
        
        periodo_frame = tk.Frame(form_frame, bg=WHITE_COLOR)
        periodo_frame.grid(row=2, column=1, sticky='w', padx=10, pady=4)

        self.combo_periodo = ttk.Combobox(periodo_frame, values=["febrero-junio", "agosto-diciembre"], state='readonly', width=20)
        self.combo_periodo.pack(side='left', padx=(0, 5))

        ttk.Label(periodo_frame, text="Año:", style='Content.TLabel', background=WHITE_COLOR).pack(side='left', padx=5)

        self.anio_var = tk.StringVar()
        vcmd_anio = (self.register(self._solo_anio), '%P')
        ttk.Entry(periodo_frame, textvariable=self.anio_var, width=10, validate='key', validatecommand=vcmd_anio).pack(side='left')

        ttk.Label(form_frame, text="Nota (0-100):", style='Content.TLabel').grid(row=3, column=0, sticky='w', pady=4)
        self.nota_var = tk.StringVar()
        vcmd_nums = (self.register(self._solo_nums_punto), '%P')
        ttk.Entry(form_frame, textvariable=self.nota_var, width=10,
                  validate='key', validatecommand=vcmd_nums).grid(row=3, column=1, sticky='w', padx=10, pady=4)

        btn_form = tk.Frame(form_frame, bg=WHITE_COLOR)
        btn_form.grid(row=4, column=0, columnspan=2, pady=10)

        # Botón dinámico: "Registrar" o "Actualizar Nota"
        self.btn_accion = ttk.Button(btn_form, text="Registrar", command=self.guardar)
        self.btn_accion.pack(side='left', padx=5)
        ttk.Button(btn_form, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=5)

        # --- Treeview ---
        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columnas = ("ID", "Alumno", "Materia", "Periodo", "Nota")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)

        anchos = {"ID": 40, "Alumno": 200, "Materia": 180, "Periodo": 100, "Nota": 70}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 100), anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

    # ── Validación ────────────────────────────────────────────────────────────

    def _solo_nums_punto(self, val: str) -> bool:
        """Permite dígitos y un solo punto decimal."""
        if val == "":
            return True
        try:
            parts = val.split('.')
            if len(parts) > 2:
                return False
            return all(p.isdigit() for p in parts if p)
        except Exception:
            return False

    def _solo_anio(self, val: str) -> bool:
        """Permite solo dígitos y un máximo de 4 caracteres."""
        if val == "":
            return True
        return val.isdigit() and len(val) <= 4

    # ── Datos ─────────────────────────────────────────────────────────────────

    def cargar_datos_iniciales(self):
        try:
            alumnos  = AlumnoService.listar_todos()
            materias = MateriaService.listar_todos()
            self.mapa_alumnos  = {f"{a.matricula} - {a.nombre}": a.id for a in alumnos}
            self.mapa_materias = {f"{m.clave} - {m.nombre}": m.id for m in materias}
            self.combo_alumnos['values']  = list(self.mapa_alumnos.keys())
            self.combo_materias['values'] = list(self.mapa_materias.keys())
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def cargar_calificaciones(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            for c in CalificacionRepository.obtener_calificaciones_join():
                self.tree.insert("", "end", values=(
                    c['id_calificacion'], c['nombre_alumno'],
                    c['nombre_materia'],  c['periodo'], c['nota']
                ))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def seleccionar_registro(self, _event=None):
        """Carga la fila seleccionada en el formulario para su posible edición."""
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], 'values')
        self.calificacion_id_actual = int(v[0])

        self.nota_var.set(str(v[4]))
        nombre_alumno  = v[1]
        nombre_materia = v[2]
        
        # Parsear el periodo
        periodo_completo = str(v[3])
        parts = periodo_completo.split(" ")
        if len(parts) == 2:
            self.combo_periodo.set(parts[0])
            self.anio_var.set(parts[1])
        else:
            self.combo_periodo.set("")
            self.anio_var.set("")

        # Seleccionar el combo más cercano al alumno/materia mostrado
        for k in self.mapa_alumnos:
            if nombre_alumno in k:
                self.combo_alumnos.set(k)
                break
        for k in self.mapa_materias:
            if nombre_materia in k:
                self.combo_materias.set(k)
                break

        # Cambiar botón a modo UPDATE
        self.btn_accion.config(text="Actualizar Calificación")

    def guardar(self):
        """INSERT si no hay selección, UPDATE si la hay."""
        nota_str = self.nota_var.get().strip()

        if not nota_str:
            messagebox.showwarning("CAMPO VACÍO", "Ingrese una nota.")
            return

        try:
            nota = float(nota_str)
        except ValueError:
            messagebox.showwarning("ERROR", "La nota debe ser un número válido.")
            return

        sel_alumno  = self.combo_alumnos.get()
        sel_materia = self.combo_materias.get()
        semestre    = self.combo_periodo.get()
        anio        = self.anio_var.get().strip()
        
        periodo = f"{semestre} {anio}" if semestre and anio else ""

        if not all([sel_alumno, sel_materia, semestre, anio]):
            messagebox.showwarning("CAMPOS VACÍOS", "Alumno, Materia, Semestre y Año son obligatorios.")
            return
            
        if len(anio) != 4:
            messagebox.showwarning("AÑO INVÁLIDO", "El año debe tener 4 dígitos.")
            return

        try:
            alumno_id  = self.mapa_alumnos[sel_alumno]
            materia_id = self.mapa_materias[sel_materia]
            
            usuario_id = self.usuario.id if self.usuario else 0
            
            # ── Modo UPDATE ──
            if self.calificacion_id_actual is not None:
                CalificacionService.modificar_calificacion(self.calificacion_id_actual, alumno_id, materia_id, periodo, nota, usuario_id)
                messagebox.showinfo("ÉXITO", "Calificación actualizada correctamente.")
            else:
                # ── Modo INSERT ──
                CalificacionService.registrar_calificacion(alumno_id, materia_id, periodo, nota, usuario_id)
                messagebox.showinfo("ÉXITO", "Calificación registrada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_calificaciones()
        except ValueError as ve:
            messagebox.showerror("REGLA DE NEGOCIO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def limpiar_formulario(self):
        self.calificacion_id_actual = None
        self.combo_alumnos.set("")
        self.combo_materias.set("")
        self.combo_periodo.set("")
        self.anio_var.set("")
        self.nota_var.set("")
        self.btn_accion.config(text="Registrar")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
