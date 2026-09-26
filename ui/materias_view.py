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
        
        # Botón rojo para eliminar físicamente usando tk.Button nativo para color personalizado
        btn_eliminar = tk.Button(btn_frame, text="Eliminar", bg="#d9534f", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.eliminar)
        btn_eliminar.pack(side='right', padx=5, ipady=3, ipadx=10)

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

    def eliminar(self):
        if self.materia_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione una materia primero.")
            return
            
        respuesta = messagebox.askyesno("CONFIRMAR", "¿Está seguro de que desea eliminar este registro permanentemente? Esta acción es irreversible.")
        if not respuesta:
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
