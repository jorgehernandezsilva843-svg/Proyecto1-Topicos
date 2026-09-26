import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR, PRIMARY_COLOR
from models.domain import Alumno
from services.alumno_service import AlumnoService

# Ruta al logo institucional
_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")


class AlumnosView(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=WHITE_COLOR)
        self.alumno_id_actual = None
        self.alumnos_en_memoria = []
        self._logo_img = None          # referencia para evitar que el GC la elimine
        self._build_ui()
        self._poner_fondo()
        self.cargar_datos()

    # ── Fondo con logo institucional ──────────────────────────────────────────

    def _poner_fondo(self):
        """Coloca el logo institucional semitransparente centrado al fondo."""
        try:
            from PIL import Image, ImageTk
            img = Image.open(_LOGO_PATH).convert("RGBA")
            # Aplicar opacidad del 12 %
            r, g, b, a = img.split()
            a = a.point(lambda p: int(p * 0.12))
            img.putalpha(a)
            img = img.convert("RGBA")
            img = img.resize((340, 340), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
        except ImportError:
            # Pillow no disponible: usar imagen normal sin opacidad
            try:
                img = tk.PhotoImage(file=_LOGO_PATH)
                self._logo_img = img
            except Exception:
                return
        except Exception:
            return

        lbl = tk.Label(self, image=self._logo_img, bg=WHITE_COLOR, bd=0)
        lbl.place(relx=0.5, rely=0.55, anchor='center')
        lbl.lower()   # enviar al fondo de la pila Z

    # ── Construcción de la interfaz ───────────────────────────────────────────

    def _build_ui(self):
        ttk.Label(self, text="GESTIÓN DE ALUMNOS", style='Title.TLabel').pack(pady=(10, 15))

        # --- Buscador ---
        search_frame = tk.Frame(self, bg=WHITE_COLOR)
        search_frame.pack(fill='x', padx=20, pady=4)

        ttk.Label(search_frame, text="Buscar (Nombre/Matrícula):", style='Content.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="Mostrar Todos", command=self.cargar_datos).pack(side='left', padx=5)

        # --- Treeview ---
        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=8)

        columnas = ("ID", "Matrícula", "Nombre", "Correo", "Grupo", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=8)

        anchos = {"ID": 40, "Matrícula": 90, "Nombre": 160, "Correo": 200, "Grupo": 70, "Estado": 80}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 100), anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        # Selección carga el formulario automáticamente
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        # --- Formulario con validaciones ---
        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=4)

        vcmd_letras  = (self.register(self._solo_letras),   '%P')
        vcmd_alfanum = (self.register(self._alfanumerico),  '%P')

        self.matricula_var = tk.StringVar()
        self.nombre_var    = tk.StringVar()
        self.correo_var    = tk.StringVar()
        self.grupo_var     = tk.StringVar()

        campos = [
            ("Matrícula:",  self.matricula_var, vcmd_alfanum),
            ("Nombre:",     self.nombre_var,    vcmd_letras),
            ("Correo:",     self.correo_var,    None),         # correo libre
            ("Grupo:",      self.grupo_var,     vcmd_alfanum),
        ]
        for i, (label, var, vcmd) in enumerate(campos):
            ttk.Label(form_frame, text=label, style='Content.TLabel').grid(row=i, column=0, sticky='w', pady=3)
            kwargs = dict(textvariable=var, width=42)
            if vcmd:
                kwargs.update(validate='key', validatecommand=vcmd)
            ttk.Entry(form_frame, **kwargs).grid(row=i, column=1, padx=10, pady=3)

        # --- Botones ---
        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(6, 12))

        # El texto del botón "Guardar" indica la acción actual (INSERT / UPDATE)
        self.btn_guardar = ttk.Button(btn_frame, text="Guardar (Nuevo)", command=self.guardar)
        self.btn_guardar.pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Eliminar", bg="#d9534f", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self.eliminar).pack(side='right', padx=5, ipady=3, ipadx=10)

        self.btn_toggle = ttk.Button(btn_frame, text="Desactivar", command=self.alternar_estado)
        self.btn_toggle.pack(side='right', padx=5)

    # ── Validaciones de entrada ───────────────────────────────────────────────

    def _solo_letras(self, val: str) -> bool:
        return all(c.isalpha() or c.isspace() for c in val) or val == ""

    def _alfanumerico(self, val: str) -> bool:
        return all(c.isalnum() for c in val) or val == ""

    # ── Lógica de datos ───────────────────────────────────────────────────────

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.alumnos_en_memoria = AlumnoService.listar_todos()
            self._poblar_tree(self.alumnos_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def _poblar_tree(self, lista):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for a in lista:
            try:
                es_activo = int(a.activo) == 1
            except (ValueError, TypeError):
                es_activo = False
            estado = "ACTIVO" if es_activo else "INACTIVO"
            self.tree.insert("", "end", values=(a.id, a.matricula, a.nombre, a.correo, a.grupo, estado))

    def filtrar(self):
        t = self.search_var.get().strip().lower()
        if not t:
            return
        self._poblar_tree([a for a in self.alumnos_en_memoria
                           if t in a.nombre.lower() or t in a.matricula.lower()])

    def seleccionar_registro(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], 'values')
        self.alumno_id_actual = int(v[0])
        self.matricula_var.set(v[1])
        self.nombre_var.set(v[2])
        self.correo_var.set(v[3])
        self.grupo_var.set(v[4])

        estado_actual = v[5]
        self.btn_toggle.config(text="Desactivar" if estado_actual == "ACTIVO" else "Activar")
        # Botón indica modo UPDATE
        self.btn_guardar.config(text="Guardar (Actualizar)")

    # ── Guardar: INSERT si es nuevo, UPDATE si hay selección ─────────────────

    def guardar(self):
        matricula = self.matricula_var.get().strip()
        nombre    = self.nombre_var.get().strip()
        correo    = self.correo_var.get().strip()
        grupo     = self.grupo_var.get().strip()

        if not all([matricula, nombre, correo, grupo]):
            messagebox.showwarning("CAMPOS VACÍOS", "Todos los campos son obligatorios.")
            return

        alumno = Alumno(id=self.alumno_id_actual, matricula=matricula,
                        nombre=nombre, correo=correo, grupo=grupo)
        try:
            if self.alumno_id_actual is None:
                AlumnoService.insertar(alumno)
                messagebox.showinfo("ÉXITO", "Alumno registrado correctamente.")
            else:
                AlumnoService.actualizar(alumno)
                messagebox.showinfo("ÉXITO", "Alumno actualizado correctamente.")
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def alternar_estado(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione un alumno primero.")
            return
        accion = self.btn_toggle.cget("text")
        if not messagebox.askyesno("CONFIRMAR", f"¿Desea {accion.lower()} al alumno?"):
            return
        try:
            AlumnoService.alternar_estado(self.alumno_id_actual)
            messagebox.showinfo("ÉXITO", f"Alumno {accion.lower()}do correctamente.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def eliminar(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione un alumno primero.")
            return
        if not messagebox.askyesno("CONFIRMAR",
                "¿Está seguro de que desea eliminar este registro permanentemente? Esta acción es irreversible."):
            return
        try:
            AlumnoService.eliminar_registro(self.alumno_id_actual)
            messagebox.showinfo("ÉXITO", "Alumno eliminado permanentemente.")
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
        self.btn_toggle.config(text="Desactivar")
        self.btn_guardar.config(text="Guardar (Nuevo)")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
