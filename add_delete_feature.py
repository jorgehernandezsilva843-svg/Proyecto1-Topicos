import os

BASE_DIR = r"C:\Users\Administrador\Desktop\Fund. & Simulación\Proyecto1 Topicos"

def append_to_file(rel_path, content):
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)

def replace_in_file(rel_path, old_text, new_text):
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_text, new_text)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Repositories - Add physical delete (DELETE FROM)
repo_alumno_code = """
    @staticmethod
    def eliminar_fisicamente(alumno_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alumnos WHERE id = ?', (alumno_id,))
        conn.commit()
        conn.close()
"""
append_to_file(r"repositories\alumno_repository.py", repo_alumno_code)

repo_materia_code = """
    @staticmethod
    def eliminar_fisicamente(materia_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM materias WHERE id = ?', (materia_id,))
        conn.commit()
        conn.close()
"""
append_to_file(r"repositories\materia_repository.py", repo_materia_code)

# 2. Services - Add logic enforcing integrity
srv_alumno_code = """
    @staticmethod
    def eliminar_registro(alumno_id: int):
        if CalificacionRepository.existe_por_alumno(alumno_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        AlumnoRepository.eliminar_fisicamente(alumno_id)
"""
append_to_file(r"services\alumno_service.py", srv_alumno_code)

srv_materia_code = """
    @staticmethod
    def eliminar_registro(materia_id: int):
        if CalificacionRepository.existe_por_materia(materia_id):
            raise ValueError("Error de integridad: No se puede eliminar porque tiene calificaciones registradas. Utilice la opción de desactivar.")
        MateriaRepository.eliminar_fisicamente(materia_id)
"""
append_to_file(r"services\materia_service.py", srv_materia_code)

# 3. UI Views - Add Red Delete button and confirmation logic
old_btn = """ttk.Button(btn_frame, text="Desactivar", command=self.desactivar).pack(side='right', padx=5)"""
new_btn = """ttk.Button(btn_frame, text="Desactivar", command=self.desactivar).pack(side='right', padx=5)
        
        # Botón rojo para eliminar físicamente usando tk.Button nativo para color personalizado
        btn_eliminar = tk.Button(btn_frame, text="Eliminar", bg="#d9534f", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.eliminar)
        btn_eliminar.pack(side='right', padx=5, ipady=3, ipadx=10)"""

replace_in_file(r"ui\alumnos_view.py", old_btn, new_btn)
replace_in_file(r"ui\materias_view.py", old_btn, new_btn)

# Add eliminar method to AlumnosView
old_limpiar_alumnos = """        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())"""
new_limpiar_alumnos = """        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def eliminar(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "Seleccione un alumno primero.")
            return
            
        respuesta = messagebox.askyesno("CONFIRMAR", "¿Está seguro de que desea eliminar este registro permanentemente? Esta acción es irreversible.")
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
            messagebox.showerror("ERROR", str(e))"""

replace_in_file(r"ui\alumnos_view.py", old_limpiar_alumnos, new_limpiar_alumnos)

# Add eliminar method to MateriasView
new_limpiar_materias = """        if self.tree.selection():
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
            messagebox.showerror("ERROR", str(e))"""

replace_in_file(r"ui\materias_view.py", old_limpiar_alumnos, new_limpiar_materias)

print("Modificación completada: Funcionalidad de eliminación física agregada.")
