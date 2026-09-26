import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from models.domain import Materia
from services.materia_service import MateriaService

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")


class MateriasView(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master, bg=WHITE_COLOR)
        self.usuario = usuario
        self.materia_id_actual = None
        self.materias_en_memoria = []
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        self.cargar_datos()

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
        lbl.place(relx=0.5, rely=0.55, anchor='center')
        lbl.lower()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        ttk.Label(self, text="GESTIÓN DE MATERIAS", style='Title.TLabel').pack(pady=(10, 15))

        search_frame = tk.Frame(self, bg=WHITE_COLOR)
        search_frame.pack(fill='x', padx=20, pady=4)
        ttk.Label(search_frame, text="Buscar (Nombre/Clave):", style='Content.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="Mostrar Todas", command=self.cargar_datos).pack(side='left', padx=5)

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=8)

        columnas = ("ID", "Clave", "Nombre", "Créditos", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=8)
        anchos = {"ID": 40, "Clave": 90, "Nombre": 200, "Créditos": 80, "Estado": 80}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 100), anchor='center')
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=4)

        vcmd_letras  = (self.register(self._solo_letras),  '%P')
        vcmd_alfanum = (self.register(self._alfanumerico), '%P')
        vcmd_nums    = (self.register(self._solo_nums),    '%P')

        self.clave_var    = tk.StringVar()
        self.nombre_var   = tk.StringVar()
        self.creditos_var = tk.StringVar()

        campos = [
            ("Clave:",     self.clave_var,    vcmd_alfanum),
            ("Nombre:",    self.nombre_var,   vcmd_letras),
            ("Créditos:",  self.creditos_var, vcmd_nums),
        ]
        for i, (label, var, vcmd) in enumerate(campos):
            ttk.Label(form_frame, text=label, style='Content.TLabel').grid(row=i, column=0, sticky='w', pady=3)
            kwargs = dict(textvariable=var, width=40)
            if vcmd:
                kwargs.update(validate='key', validatecommand=vcmd)
            ttk.Entry(form_frame, **kwargs).grid(row=i, column=1, padx=10, pady=3)

        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(6, 12))

        self.btn_guardar = ttk.Button(btn_frame, text="Guardar (Nueva)", command=self.guardar)
        self.btn_guardar.pack(side='left', padx=5)
        self.btn_limpiar = ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario)
        self.btn_limpiar.pack(side='left', padx=5)

        self.btn_eliminar = tk.Button(btn_frame, text="Eliminar", bg="#d9534f", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self.eliminar)
        self.btn_eliminar.pack(side='right', padx=5, ipady=3, ipadx=10)

        self.btn_toggle = ttk.Button(btn_frame, text="Desactivar", command=self.alternar_estado)
        self.btn_toggle.pack(side='right', padx=5)

        if self.usuario and self.usuario.rol.lower() == 'operador':
            self.btn_guardar.pack_forget()
            self.btn_limpiar.pack_forget()
            self.btn_eliminar.pack_forget()
            self.btn_toggle.pack_forget()

    # ── Validaciones ─────────────────────────────────────────────────────────

    def _solo_letras(self, val):
        return all(c.isalpha() or c.isspace() for c in val) or val == ""

    def _alfanumerico(self, val):
        return all(c.isalnum() for c in val) or val == ""

    def _solo_nums(self, val):
        return val.isdigit() or val == ""

    # ── Datos ─────────────────────────────────────────────────────────────────

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.materias_en_memoria = MateriaService.listar_todos()
            self._poblar_tree(self.materias_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def _poblar_tree(self, lista):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for m in lista:
            try:
                es_activa = int(m.activo) == 1
            except (ValueError, TypeError):
                es_activa = False
            estado = "ACTIVA" if es_activa else "INACTIVA"
            self.tree.insert("", "end", values=(m.id, m.clave, m.nombre, m.creditos, estado))

    def filtrar(self):
        t = self.search_var.get().strip().lower()
        if not t:
            return
        self._poblar_tree([m for m in self.materias_en_memoria
                           if t in m.nombre.lower() or t in m.clave.lower()])

    def seleccionar_registro(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], 'values')
        self.materia_id_actual = int(v[0])
        self.clave_var.set(v[1])
        self.nombre_var.set(v[2])
        self.creditos_var.set(v[3])

        self.btn_toggle.config(text="Desactivar" if v[4] == "ACTIVA" else "Activar")
        self.btn_guardar.config(text="Guardar (Actualizar)")

    def guardar(self):
        clave    = self.clave_var.get().strip()
        nombre   = self.nombre_var.get().strip()
        cred_str = self.creditos_var.get().strip()

        if not all([clave, nombre, cred_str]):
            messagebox.showwarning("CAMPOS VACÍOS", "Todos los campos son obligatorios.")
            return

        materia = Materia(id=self.materia_id_actual, clave=clave, nombre=nombre, creditos=int(cred_str))
        try:
            if self.materia_id_actual is None:
                MateriaService.insertar(materia)
                messagebox.showinfo("ÉXITO", "Materia registrada correctamente.")
            else:
                MateriaService.actualizar(materia)
                messagebox.showinfo("ÉXITO", "Materia actualizada correctamente.")
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def alternar_estado(self):
        if self.materia_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione una materia primero.")
            return
        accion = self.btn_toggle.cget("text")
        if not messagebox.askyesno("CONFIRMAR", f"¿Desea {accion.lower()} la materia?"):
            return
        try:
            MateriaService.alternar_estado(self.materia_id_actual)
            messagebox.showinfo("ÉXITO", f"Materia {accion.lower()}da correctamente.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def eliminar(self):
        if self.materia_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione una materia primero.")
            return
        if not messagebox.askyesno("CONFIRMAR",
                "¿Está seguro de que desea eliminar este registro permanentemente? Esta acción es irreversible."):
            return
        try:
            MateriaService.eliminar_registro(self.materia_id_actual)
            messagebox.showinfo("ÉXITO", "Materia eliminada permanentemente.")
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
        self.btn_toggle.config(text="Desactivar")
        self.btn_guardar.config(text="Guardar (Nueva)")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
