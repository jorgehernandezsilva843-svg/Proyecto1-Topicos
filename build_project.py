import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def make_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Asegurar que existan los __init__.py en las subcarpetas
    dir_name = os.path.dirname(full_path)
    if dir_name != BASE_DIR:
        init_file = os.path.join(dir_name, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'w').close()
            
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

make_file(r"db\database.py", r'''
import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'escolar.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL,
            activo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            grupo TEXT NOT NULL,
            activo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            creditos INTEGER NOT NULL,
            activo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            periodo TEXT NOT NULL,
            nota REAL NOT NULL,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias (id) ON DELETE CASCADE,
            UNIQUE(alumno_id, materia_id, periodo)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM usuarios_sistema")
    if cursor.fetchone()[0] == 0:
        username = 'admin'
        rol = 'administrador'
        estado = 'activo'
        password = 'admin123'
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        cursor.execute("""
            INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, rol, estado))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_db()
    print("Base de datos inicializada correctamente.")
''')

make_file(r"models\domain.py", r'''
from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    username: str
    rol: str
    activo: int | str
    id: Optional[int] = None

@dataclass
class Alumno:
    matricula: str
    nombre: str
    correo: str
    grupo: str
    activo: int | str = 1
    id: Optional[int] = None

@dataclass
class Materia:
    clave: str
    nombre: str
    creditos: int
    activo: int | str = 1
    id: Optional[int] = None

@dataclass
class Calificacion:
    alumno_id: int
    materia_id: int
    periodo: str
    nota: float
    id: Optional[int] = None
''')

make_file(r"repositories\alumno_repository.py", r'''
from db.database import get_connection
from models.domain import Alumno

class AlumnoRepository:
    @staticmethod
    def insertar(alumno: Alumno) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alumnos (matricula, nombre, correo, grupo, activo)
            VALUES (?, ?, ?, ?, ?)
        """, (alumno.matricula, alumno.nombre, alumno.correo, alumno.grupo, alumno.activo))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def listar_todos() -> list[Alumno]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, matricula, nombre, correo, grupo, activo FROM alumnos')
        filas = cursor.fetchall()
        conn.close()
        return [Alumno(id=f[0], matricula=f[1], nombre=f[2], correo=f[3], grupo=f[4], activo=f[5]) for f in filas]

    @staticmethod
    def actualizar(alumno: Alumno):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alumnos
            SET matricula = ?, nombre = ?, correo = ?, grupo = ?, activo = ?
            WHERE id = ?
        """, (alumno.matricula, alumno.nombre, alumno.correo, alumno.grupo, alumno.activo, alumno.id))
        conn.commit()
        conn.close()

    @staticmethod
    def desactivar(alumno_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alumnos
            SET activo = 0
            WHERE id = ?
        """, (alumno_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def obtener_por_id(alumno_id: int) -> Alumno | None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, matricula, nombre, correo, grupo, activo FROM alumnos WHERE id = ?', (alumno_id,))
        fila = cursor.fetchone()
        conn.close()
        if fila:
            return Alumno(id=fila[0], matricula=fila[1], nombre=fila[2], correo=fila[3], grupo=fila[4], activo=fila[5])
        return None
''')

make_file(r"repositories\materia_repository.py", r'''
from db.database import get_connection
from models.domain import Materia

class MateriaRepository:
    @staticmethod
    def insertar(materia: Materia) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO materias (clave, nombre, creditos, activo)
            VALUES (?, ?, ?, ?)
        """, (materia.clave, materia.nombre, materia.creditos, materia.activo))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def listar_todos() -> list[Materia]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, clave, nombre, creditos, activo FROM materias')
        filas = cursor.fetchall()
        conn.close()
        return [Materia(id=f[0], clave=f[1], nombre=f[2], creditos=f[3], activo=f[4]) for f in filas]

    @staticmethod
    def actualizar(materia: Materia):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE materias
            SET clave = ?, nombre = ?, creditos = ?, activo = ?
            WHERE id = ?
        """, (materia.clave, materia.nombre, materia.creditos, materia.activo, materia.id))
        conn.commit()
        conn.close()

    @staticmethod
    def desactivar(materia_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE materias
            SET activo = 0
            WHERE id = ?
        """, (materia_id,))
        conn.commit()
        conn.close()
''')

make_file(r"repositories\calificacion_repository.py", r'''
import sqlite3
from db.database import get_connection
from models.domain import Calificacion

class CalificacionRepository:
    @staticmethod
    def registrar_calificacion(calificacion: Calificacion) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calificaciones (alumno_id, materia_id, periodo, nota)
            VALUES (?, ?, ?, ?)
        """, (calificacion.alumno_id, calificacion.materia_id, calificacion.periodo, calificacion.nota))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

    @staticmethod
    def obtener_calificaciones_join() -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.id, 
                a.nombre AS nombre_alumno, 
                m.nombre AS nombre_materia, 
                c.periodo, 
                c.nota
            FROM calificaciones c
            INNER JOIN alumnos a ON c.alumno_id = a.id
            INNER JOIN materias m ON c.materia_id = m.id
        """)
        filas = cursor.fetchall()
        conn.close()
        
        resultados = []
        for f in filas:
            resultados.append({
                'id_calificacion': f[0],
                'nombre_alumno': f[1],
                'nombre_materia': f[2],
                'periodo': f[3],
                'nota': f[4]
            })
        return resultados

    @staticmethod
    def existe_por_alumno(alumno_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM calificaciones WHERE alumno_id = ? LIMIT 1', (alumno_id,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe

    @staticmethod
    def existe_por_materia(materia_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM calificaciones WHERE materia_id = ? LIMIT 1', (materia_id,))
        existe = cursor.fetchone() is not None
        conn.close()
        return existe
''')

make_file(r"services\usuario_service.py", r'''
import hashlib
from db.database import get_connection
from models.domain import Usuario

class UsuarioService:
    @staticmethod
    def autenticar(username: str, password: str) -> Usuario | None:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        cursor.execute('SELECT id, username, rol, activo FROM usuarios_sistema WHERE username = ? AND password_hash = ?', (username, password_hash))
        fila = cursor.fetchone()
        conn.close()
        
        if fila:
            return Usuario(id=fila[0], username=fila[1], rol=fila[2], activo=fila[3])
        return None
''')

make_file(r"services\alumno_service.py", r'''
from repositories.alumno_repository import AlumnoRepository
from repositories.calificacion_repository import CalificacionRepository
from models.domain import Alumno

class AlumnoService:
    @staticmethod
    def insertar(alumno: Alumno) -> int:
        return AlumnoRepository.insertar(alumno)
        
    @staticmethod
    def listar_todos() -> list[Alumno]:
        return AlumnoRepository.listar_todos()

    @staticmethod
    def actualizar(alumno: Alumno):
        AlumnoRepository.actualizar(alumno)

    @staticmethod
    def desactivar(alumno_id: int):
        if CalificacionRepository.existe_por_alumno(alumno_id):
            raise ValueError("No se puede desactivar un registro con movimientos activos.")
        AlumnoRepository.desactivar(alumno_id)
''')

make_file(r"services\materia_service.py", r'''
from repositories.materia_repository import MateriaRepository
from repositories.calificacion_repository import CalificacionRepository
from models.domain import Materia

class MateriaService:
    @staticmethod
    def insertar(materia: Materia) -> int:
        return MateriaRepository.insertar(materia)
        
    @staticmethod
    def listar_todos() -> list[Materia]:
        return MateriaRepository.listar_todos()

    @staticmethod
    def actualizar(materia: Materia):
        MateriaRepository.actualizar(materia)

    @staticmethod
    def desactivar(materia_id: int):
        if CalificacionRepository.existe_por_materia(materia_id):
            raise ValueError("No se puede desactivar un registro con movimientos activos.")
        MateriaRepository.desactivar(materia_id)
''')

make_file(r"services\calificacion_service.py", r'''
import sqlite3
from repositories.calificacion_repository import CalificacionRepository
from repositories.alumno_repository import AlumnoRepository
from models.domain import Calificacion

class CalificacionService:
    @staticmethod
    def registrar_calificacion(alumno_id: int, materia_id: int, periodo: str, nota: float) -> int:
        if not (0 <= nota <= 100):
            raise ValueError("La nota debe estar en el rango numérico de 0 a 100.")
            
        alumno = AlumnoRepository.obtener_por_id(alumno_id)
        if not alumno:
            raise ValueError("El alumno especificado no existe.")
            
        if str(alumno.activo) == '0' or alumno.activo == 0 or str(alumno.activo).lower() == 'inactivo':
            raise ValueError("No se puede registrar una calificación porque el alumno está inactivo.")
            
        calificacion = Calificacion(
            alumno_id=alumno_id,
            materia_id=materia_id,
            periodo=periodo,
            nota=nota
        )
        
        try:
            return CalificacionRepository.registrar_calificacion(calificacion)
        except sqlite3.IntegrityError:
            raise ValueError("El alumno ya tiene una calificación registrada para esa materia en ese periodo.")
''')

make_file(r"ui\styles.py", r'''
import tkinter as tk
from tkinter import ttk

BG_COLOR = "#000000"
FG_COLOR = "#39FF14"
WHITE_COLOR = "#FFFFFF"
FONT_RETRO = ("Courier", 12, "bold")
FONT_TITLE = ("Courier", 18, "bold")

def apply_8bit_style():
    style = ttk.Style()
    style.theme_use('default')

    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=FG_COLOR, font=FONT_RETRO)
    style.configure('TTitle.TLabel', background=BG_COLOR, foreground=WHITE_COLOR, font=FONT_TITLE)

    style.configure('TEntry', fieldbackground=BG_COLOR, foreground=FG_COLOR, font=FONT_RETRO, borderwidth=2, insertcolor=FG_COLOR, relief='solid')

    style.configure('TButton', background=BG_COLOR, foreground=FG_COLOR, font=FONT_RETRO, borderwidth=2, relief='solid')
    style.map('TButton', background=[('active', FG_COLOR), ('pressed', WHITE_COLOR)], foreground=[('active', BG_COLOR), ('pressed', BG_COLOR)])
''')

make_file(r"ui\login.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_8bit_style, BG_COLOR
from ui.main_window import MainWindow
from services.usuario_service import UsuarioService

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SISTEMA ESCOLAR - ACCESO SECRETO")
        self.geometry("450x350")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        
        apply_8bit_style()
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=30)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="=== INGRESO ===", style='TTitle.TLabel').pack(pady=(0, 30))

        ttk.Label(frame, text="USUARIO:").pack(anchor='w')
        self.entry_user = ttk.Entry(frame)
        self.entry_user.pack(fill='x', pady=(0, 15), ipady=5)

        ttk.Label(frame, text="CONTRASEÑA:").pack(anchor='w')
        self.entry_pass = ttk.Entry(frame, show="*")
        self.entry_pass.pack(fill='x', pady=(0, 30), ipady=5)

        ttk.Button(frame, text="[ ENTRAR ]", command=self.intentar_login).pack(fill='x', ipady=5)

    def intentar_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("ERROR DE SINTAXIS", "LOS CAMPOS NO PUEDEN ESTAR VACÍOS.")
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
            messagebox.showerror("ERROR FATAL DEL SISTEMA", str(e))
''')

make_file(r"ui\main_window.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import apply_8bit_style, BG_COLOR, FG_COLOR
from ui.alumnos_view import AlumnosView
from ui.materias_view import MateriasView
from ui.calificaciones_view import CalificacionesView
from ui.reportes_view import ReportesView

class MainWindow(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.title("PANEL DE COMANDOS - SISTEMA ESCOLAR")
        self.geometry("800x600")
        self.configure(bg=BG_COLOR)
        
        apply_8bit_style()
        self._build_menu()
        self._build_ui()

    def _build_menu(self):
        menu_bar = tk.Menu(self, bg=BG_COLOR, fg=FG_COLOR, font=("Courier", 10, "bold"), activebackground=FG_COLOR, activeforeground=BG_COLOR, relief='solid')
        
        modulos_menu = tk.Menu(menu_bar, tearoff=0, bg=BG_COLOR, fg=FG_COLOR, activebackground=FG_COLOR, activeforeground=BG_COLOR, font=("Courier", 10))
                               
        modulos_menu.add_command(label="> ALUMNOS", command=lambda: AlumnosView(self))
        modulos_menu.add_command(label="> MATERIAS", command=lambda: MateriasView(self))
        modulos_menu.add_command(label="> CALIFICACIONES", command=lambda: CalificacionesView(self))
        modulos_menu.add_command(label="> REPORTES", command=lambda: ReportesView(self))
        modulos_menu.add_separator()
        modulos_menu.add_command(label="[ CERRAR SESIÓN ]", command=self.cerrar_sesion)
        modulos_menu.add_command(label="[ SALIR DEL SISTEMA ]", command=self.destroy)
        
        menu_bar.add_cascade(label="MÓDULOS", menu=modulos_menu)
        self.config(menu=menu_bar)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(expand=True, fill='both')

        info_text = f"SESIÓN ACTIVA\n\nUSUARIO: {self.usuario.username}\nROL: {self.usuario.rol.upper()}"
        ttk.Label(frame, text=info_text, style='TTitle.TLabel', justify='center').pack(pady=40)

        retro_art = """
           ___  ___  _  _  ___  ___  _     
          / __|/ __|| || |/ _ \/ _ \| |    
          \__ \ (__ | __ | (_) |(_) | |__  
          |___/\___||_||_|\___/ \___/|____|
          
          EN ESPERA DE INSTRUCCIONES...
          _
        """
        tk.Label(frame, text=retro_art, bg=BG_COLOR, fg=FG_COLOR, font=("Courier", 12), justify='left').pack(pady=20)

    def cerrar_sesion(self):
        self.destroy()
        from ui.login import LoginWindow
        app = LoginWindow()
        app.mainloop()
''')

make_file(r"ui\alumnos_view.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import BG_COLOR, FG_COLOR
from models.domain import Alumno
from services.alumno_service import AlumnoService

class AlumnosView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("MÓDULO ALUMNOS - 8 BITS")
        self.geometry("900x700")
        self.configure(bg=BG_COLOR)
        self.grab_set() 
        self.focus()

        self.alumno_id_actual = None
        self.alumnos_en_memoria = []

        self._configurar_treeview_retro()
        self._build_ui()
        self.cargar_datos()

    def _configurar_treeview_retro(self):
        style = ttk.Style()
        style.configure("Treeview", background=BG_COLOR, foreground=FG_COLOR, fieldbackground=BG_COLOR, font=("Courier", 10))
        style.configure("Treeview.Heading", background=BG_COLOR, foreground=FG_COLOR, font=("Courier", 11, "bold"), relief="solid", borderwidth=2)
        style.map("Treeview", background=[('selected', FG_COLOR)], foreground=[('selected', BG_COLOR)])

    def _build_ui(self):
        search_frame = tk.Frame(self, bg=BG_COLOR)
        search_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(search_frame, text="BUSCAR (NOMBRE/MATRÍCULA):").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="[ FILTRAR ]", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="[ MOSTRAR TODOS ]", command=self.cargar_datos).pack(side='left', padx=5)

        tree_frame = tk.Frame(self, bg=BG_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20)

        columnas = ("ID", "Matrícula", "Nombre", "Correo", "Grupo", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, bg=BG_COLOR)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(fill='x', padx=20, pady=20)

        self.matricula_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.correo_var = tk.StringVar()
        self.grupo_var = tk.StringVar()

        campos = [
            ("MATRÍCULA:", self.matricula_var),
            ("NOMBRE:", self.nombre_var),
            ("CORREO:", self.correo_var),
            ("GRUPO:", self.grupo_var)
        ]

        for i, (label_text, var) in enumerate(campos):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=5)
            ttk.Entry(form_frame, textvariable=var, width=50).grid(row=i, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Button(btn_frame, text="[ GUARDAR ]", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="[ LIMPIAR ]", command=self.limpiar_formulario).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="[ DESACTIVAR ]", command=self.desactivar).pack(side='right', padx=5)

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.alumnos_en_memoria = AlumnoService.listar_todos()
            self._actualizar_treeview(self.alumnos_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", f"FALLO AL CARGAR DATOS:\n{e}")

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
            messagebox.showwarning("ADVERTENCIA", "TODOS LOS CAMPOS SON OBLIGATORIOS.")
            return

        alumno = Alumno(id=self.alumno_id_actual, matricula=matricula, nombre=nombre, correo=correo, grupo=grupo)

        try:
            if self.alumno_id_actual is None:
                AlumnoService.insertar(alumno)
                messagebox.showinfo("ÉXITO", "ALUMNO REGISTRADO CORRECTAMENTE.")
            else:
                AlumnoService.actualizar(alumno)
                messagebox.showinfo("ÉXITO", "ALUMNO ACTUALIZADO CORRECTAMENTE.")
                
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR DE SISTEMA", f"NO SE PUDO GUARDAR:\n{str(e)}")

    def desactivar(self):
        if self.alumno_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "SELECCIONE UN ALUMNO DE LA LISTA PRIMERO.")
            return

        respuesta = messagebox.askyesno("CONFIRMAR", "¿ESTÁ SEGURO DE DESACTIVAR AL ALUMNO?")
        if not respuesta:
            return

        try:
            AlumnoService.desactivar(self.alumno_id_actual)
            messagebox.showinfo("ÉXITO", "ALUMNO DESACTIVADO CORRECTAMENTE.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR INESPERADO", str(e))

    def limpiar_formulario(self):
        self.alumno_id_actual = None
        self.matricula_var.set("")
        self.nombre_var.set("")
        self.correo_var.set("")
        self.grupo_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
''')

make_file(r"ui\materias_view.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import BG_COLOR, FG_COLOR
from models.domain import Materia
from services.materia_service import MateriaService

class MateriasView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("MÓDULO MATERIAS - 8 BITS")
        self.geometry("800x600")
        self.configure(bg=BG_COLOR)
        self.grab_set() 
        self.focus()

        self.materia_id_actual = None
        self.materias_en_memoria = []

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        search_frame = tk.Frame(self, bg=BG_COLOR)
        search_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(search_frame, text="BUSCAR (NOMBRE/CLAVE):").pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=10, fill='x', expand=True)
        ttk.Button(search_frame, text="[ FILTRAR ]", command=self.filtrar).pack(side='left')
        ttk.Button(search_frame, text="[ MOSTRAR TODAS ]", command=self.cargar_datos).pack(side='left', padx=5)

        tree_frame = tk.Frame(self, bg=BG_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20)

        columnas = ("ID", "Clave", "Nombre", "Créditos", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=8)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_registro)
        
        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, bg=BG_COLOR)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(fill='x', padx=20, pady=20)

        self.clave_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.creditos_var = tk.StringVar()

        campos = [
            ("CLAVE:", self.clave_var),
            ("NOMBRE:", self.nombre_var),
            ("CRÉDITOS:", self.creditos_var)
        ]

        for i, (label_text, var) in enumerate(campos):
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky='w', pady=5)
            ttk.Entry(form_frame, textvariable=var, width=40).grid(row=i, column=1, padx=10, pady=5)

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Button(btn_frame, text="[ GUARDAR ]", command=self.guardar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="[ LIMPIAR ]", command=self.limpiar_formulario).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="[ DESACTIVAR ]", command=self.desactivar).pack(side='right', padx=5)

    def cargar_datos(self):
        try:
            self.search_var.set("")
            self.materias_en_memoria = MateriaService.listar_todos()
            self._actualizar_treeview(self.materias_en_memoria)
        except Exception as e:
            messagebox.showerror("ERROR", f"FALLO AL CARGAR DATOS:\n{e}")

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
            messagebox.showwarning("ADVERTENCIA", "TODOS LOS CAMPOS SON OBLIGATORIOS.")
            return
            
        if not creditos_str.isdigit():
            messagebox.showwarning("ERROR DE SINTAXIS", "LOS CRÉDITOS DEBEN SER UN NÚMERO ENTERO.")
            return

        materia = Materia(id=self.materia_id_actual, clave=clave, nombre=nombre, creditos=int(creditos_str))

        try:
            if self.materia_id_actual is None:
                MateriaService.insertar(materia)
                messagebox.showinfo("ÉXITO", "MATERIA REGISTRADA.")
            else:
                MateriaService.actualizar(materia)
                messagebox.showinfo("ÉXITO", "MATERIA ACTUALIZADA.")
                
            self.limpiar_formulario()
            self.cargar_datos()
        except Exception as e:
            messagebox.showerror("ERROR DE SISTEMA", f"NO SE PUDO GUARDAR:\n{str(e)}")

    def desactivar(self):
        if self.materia_id_actual is None:
            messagebox.showwarning("ATENCIÓN", "SELECCIONE UNA MATERIA PRIMERO.")
            return

        respuesta = messagebox.askyesno("CONFIRMAR", "¿ESTÁ SEGURO DE DESACTIVAR LA MATERIA?")
        if not respuesta:
            return

        try:
            MateriaService.desactivar(self.materia_id_actual)
            messagebox.showinfo("ÉXITO", "MATERIA DESACTIVADA CORRECTAMENTE.")
            self.limpiar_formulario()
            self.cargar_datos()
        except ValueError as ve:
            messagebox.showerror("DENEGADO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR INESPERADO", str(e))

    def limpiar_formulario(self):
        self.materia_id_actual = None
        self.clave_var.set("")
        self.nombre_var.set("")
        self.creditos_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
''')

make_file(r"ui\calificaciones_view.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import BG_COLOR, FG_COLOR
from services.alumno_service import AlumnoService
from services.materia_service import MateriaService
from services.calificacion_service import CalificacionService
from repositories.calificacion_repository import CalificacionRepository

class CalificacionesView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("REGISTRO DE CALIFICACIONES - 8 BITS")
        self.geometry("900x700")
        self.configure(bg=BG_COLOR)
        self.grab_set()
        self.focus()

        self.mapa_alumnos = {}
        self.mapa_materias = {}

        self._build_ui()
        self.cargar_datos_iniciales()
        self.cargar_calificaciones()

    def _build_ui(self):
        form_frame = tk.Frame(self, bg=BG_COLOR)
        form_frame.pack(fill='x', padx=20, pady=20)

        ttk.Label(form_frame, text="ALUMNO:").grid(row=0, column=0, sticky='w', pady=5)
        self.combo_alumnos = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_alumnos.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="MATERIA:").grid(row=1, column=0, sticky='w', pady=5)
        self.combo_materias = ttk.Combobox(form_frame, state='readonly', width=45)
        self.combo_materias.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="PERIODO (Ej. 2023-1):").grid(row=2, column=0, sticky='w', pady=5)
        self.periodo_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.periodo_var, width=20).grid(row=2, column=1, sticky='w', padx=10, pady=5)

        ttk.Label(form_frame, text="NOTA (0-100):").grid(row=3, column=0, sticky='w', pady=5)
        self.nota_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nota_var, width=10).grid(row=3, column=1, sticky='w', padx=10, pady=5)

        ttk.Button(form_frame, text="[ REGISTRAR NOTA ]", command=self.registrar).grid(row=4, column=0, columnspan=2, pady=15)

        tree_frame = tk.Frame(self, bg=BG_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columnas = ("ID", "Alumno", "Materia", "Periodo", "Nota")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=10)
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, bg=BG_COLOR)
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
            messagebox.showerror("ERROR DE SISTEMA", str(e))

    def cargar_calificaciones(self):
        for fila in self.tree.get_children():
            self.tree.delete(fila)
            
        try:
            calificaciones = CalificacionRepository.obtener_calificaciones_join()
            for c in calificaciones:
                self.tree.insert("", "end", values=(c['id_calificacion'], c['nombre_alumno'], c['nombre_materia'], c['periodo'], c['nota']))
        except Exception as e:
            messagebox.showerror("ERROR DE LECTURA", str(e))

    def registrar(self):
        seleccion_alumno = self.combo_alumnos.get()
        seleccion_materia = self.combo_materias.get()
        periodo = self.periodo_var.get().strip()
        nota_str = self.nota_var.get().strip()

        if not all([seleccion_alumno, seleccion_materia, periodo, nota_str]):
            messagebox.showwarning("SINTAXIS ERROR", "TODOS LOS CAMPOS SON REQUERIDOS.")
            return

        try:
            nota = float(nota_str)
            alumno_id = self.mapa_alumnos[seleccion_alumno]
            materia_id = self.mapa_materias[seleccion_materia]

            CalificacionService.registrar_calificacion(alumno_id, materia_id, periodo, nota)
            
            messagebox.showinfo("ÉXITO", "CALIFICACIÓN REGISTRADA.")
            self.periodo_var.set("")
            self.nota_var.set("")
            self.cargar_calificaciones()
            
        except ValueError as ve:
            messagebox.showerror("REGLA DE NEGOCIO", str(ve))
        except Exception as e:
            messagebox.showerror("ERROR CRÍTICO", str(e))
''')

make_file(r"ui\reportes_view.py", r'''
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import BG_COLOR, FG_COLOR
from repositories.calificacion_repository import CalificacionRepository

class ReportesView(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("REPORTE DE REPROBADOS Y PROMEDIOS - 8 BITS")
        self.geometry("800x500")
        self.configure(bg=BG_COLOR)
        self.grab_set()

        self._build_ui()
        self.generar_reporte()

    def _build_ui(self):
        ttk.Label(self, text="BOLETA DE ALUMNOS REPROBADOS (< 70)", style='TTitle.TLabel').pack(pady=20)

        tree_frame = tk.Frame(self, bg=BG_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columnas = ("Alumno", "Materia Reprobada", "Nota", "Promedio General")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings")
        
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, anchor='center')

        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, bg=BG_COLOR)
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
            messagebox.showerror("ERROR AL GENERAR REPORTE", str(e))
''')

make_file(r"main.py", r'''
import sys
from db.database import inicializar_db
from ui.login import LoginWindow

def main():
    print("[SISTEMA] Inicializando motor de base de datos...")
    try:
        inicializar_db()
        print("[SISTEMA] Base de datos en línea. Llaves foráneas activas.")
    except Exception as e:
        print(f"[FATAL ERROR] Fallo al inicializar la base de datos: {e}")
        sys.exit(1)
        
    print("[SISTEMA] Arrancando interfaz gráfica (UI)...")
    app_login = LoginWindow()
    app_login.mainloop()
    print("[SISTEMA] Secuencia de apagado completada.")

if __name__ == "__main__":
    main()
''')

print("Todos los archivos del proyecto han sido creados correctamente en la carpeta de destino.")
