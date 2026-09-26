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

        # --- Buscador ---
        search_frame = tk.Frame(self, bg=WHITE_COLOR)
        search_frame.pack(fill='x', padx=20, pady=5)

        ttk.Label(search_frame, text="Buscar (Nombre/Matrícula):", style='Content.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="Filtrar", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="Mostrar Todos", command=self.cargar_datos).pack(side='left', padx=5)

        # --- Treeview ---
        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columnas = ("ID", "Matrícula", "Nombre", "Correo", "Grupo", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=9)

        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # --- Formulario con validaciones ---
        form_frame = tk.Frame(self, bg=WHITE_COLOR)
        form_frame.pack(fill='x', padx=20, pady=5)

        # Registro de comandos de validación
        vcmd_letras = (self.register(self._validar_solo_letras), '%P')
        vcmd_alfanum = (self.register(self._validar_alfanumerico), '%P')

        self.matricula_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.correo_var = tk.StringVar()
        self.grupo_var = tk.StringVar()

        ttk.Label(form_frame, text="Matrícula:", style='Content.TLabel').grid(row=0, column=0, sticky='w', pady=4)
        ttk.Entry(form_frame, textvariable=self.matricula_var, width=40,
                  validate='key', validatecommand=vcmd_alfanum).grid(row=0, column=1, padx=10, pady=4)

        ttk.Label(form_frame, text="Nombre:", style='Content.TLabel').grid(row=1, column=0, sticky='w', pady=4)
        ttk.Entry(form_frame, textvariable=self.nombre_var, width=40,
                  validate='key', validatecommand=vcmd_letras).grid(row=1, column=1, padx=10, pady=4)

        ttk.Label(form_frame, text="Correo:", style='Content.TLabel').grid(row=2, column=0, sticky='w', pady=4)
        ttk.Entry(form_frame, textvariable=self.correo_var, width=40).grid(row=2, column=1, padx=10, pady=4)

        ttk.Label(form_frame, text="Grupo:", style='Content.TLabel').grid(row=3, column=0, sticky='w', pady=4)
        ttk.Entry(form_frame, textvariable=self.grupo_var, width=40,
                  validate='key', validatecommand=vcmd_alfanum).grid(row=3, column=1, padx=10, pady=4)

        # --- Botones de acción ---
        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(8, 15))

        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario).pack(side='left', padx=5)

        # Botón eliminar (rojo, a la derecha)
        btn_eliminar = tk.Button(btn_frame, text="Eliminar", bg="#d9534f", fg="white",
                                 font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                                 command=self.eliminar)
        btn_eliminar.pack(side='right', padx=5, ipady=3, ipadx=10)

        # Botón toggle desactivar/activar (texto dinámico)
        self.btn_toggle = ttk.Button(btn_frame, text="Desactivar", command=self.alternar_estado)
        self.btn_toggle.pack(side='right', padx=5)

    # ── Funciones de validación de entrada ────────────────────────────────────

    def _validar_solo_letras(self, valor_propuesto: str) -> bool:
        """Permite únicamente letras (A-Z, a-z, acentos, ñ) y espacios."""
        return all(c.isalpha() or c.isspace() for c in valor_propuesto) or valor_propuesto == ""

    def _validar_alfanumerico(self, valor_propuesto: str) -> bool:
        """Permite letras y números, pero bloquea espacios y caracteres especiales."""
        return all(c.isalnum() for c in valor_propuesto) or valor_propuesto == ""

    # ── Lógica de datos ────────────────────────────────────────────────────────

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
            estado = "ACTIVO" if a.activo == 1 else "INACTIVO"
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

        # Actualizar texto del botón toggle según el estado actual
        estado_actual = valores[5]  # "ACTIVO" o "INACTIVO"
        if estado_actual == "ACTIVO":
            self.btn_toggle.config(text="Desactivar")
        else:
            self.btn_toggle.config(text="Activar")

    def guardar(self):
        matricula = self.matricula_var.get().strip()
        nombre = self.nombre_var.get().strip()
        correo = self.correo_var.get().strip()
        grupo = self.grupo_var.get().strip()

        if not all([matricula, nombre, correo, grupo]):
            messagebox.showwarning("CAMPOS VACÍOS", "Todos los campos son obligatorios.")
            return

        alumno = Alumno(id=self.alumno_id_actual, matricula=matricula, nombre=nombre,
                        correo=correo, grupo=grupo)
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
            messagebox.showerror("ERROR DE SISTEMA", f"No se pudo guardar:\n{str(e)}")

    def alternar_estado(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione un alumno primero.")
            return
        texto_accion = self.btn_toggle.cget("text")
        respuesta = messagebox.askyesno("CONFIRMAR", f"¿Desea {texto_accion.lower()} al alumno?")
        if not respuesta:
            return
        try:
            AlumnoService.alternar_estado(self.alumno_id_actual)
            messagebox.showinfo("ÉXITO", f"Alumno {texto_accion.lower()}do correctamente.")
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
        respuesta = messagebox.askyesno("CONFIRMAR",
            "¿Está seguro de que desea eliminar este registro permanentemente? Esta acción es irreversible.")
        if not respuesta:
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
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
