import os
import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import WHITE_COLOR
from repositories.bitacora_repository import BitacoraRepository

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_tecnm.png")

class BitacoraView(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master, bg=WHITE_COLOR)
        self.usuario = usuario
        self._logo_img = None
        self._build_ui()
        self._poner_fondo()
        self.cargar_datos()

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

    def _build_ui(self):
        ttk.Label(self, text="BITÁCORA DE ACCIONES", style='Title.TLabel').pack(pady=(10, 20))

        tree_frame = tk.Frame(self, bg=WHITE_COLOR)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=15)

        columnas = ("ID", "Usuario", "Acción Realizada", "Fecha y Hora")
        self.tree = ttk.Treeview(tree_frame, columns=columnas, show="headings", height=12)

        anchos = {"ID": 50, "Usuario": 100, "Acción Realizada": 400, "Fecha y Hora": 150}
        for col in columnas:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=anchos.get(col, 150), anchor='center' if col != "Acción Realizada" else 'w')

        self.tree.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        btn_frame = tk.Frame(self, bg=WHITE_COLOR)
        btn_frame.pack(fill='x', padx=20, pady=15)

        ttk.Button(btn_frame, text="↻ Actualizar", command=self.cargar_datos).pack(side='left', padx=5)

    def cargar_datos(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            acciones = BitacoraRepository.listar_acciones()
            for a in acciones:
                self.tree.insert("", "end", values=(a['id'], a['username'], a['accion'], a['fecha']))
        except Exception as e:
            messagebox.showerror("ERROR", str(e))
