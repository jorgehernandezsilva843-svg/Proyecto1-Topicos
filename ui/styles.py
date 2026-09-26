import tkinter as tk
from tkinter import ttk

# Paleta Institucional Moderna
PRIMARY_COLOR = "#132c54"      # Azul marino oscuro
PRIMARY_HOVER = "#1e4480"      # Azul marino claro (hover)
BG_COLOR = "#f4f4f4"           # Gris claro para áreas de trabajo
WHITE_COLOR = "#ffffff"        # Blanco puro
TEXT_DARK = "#333333"          # Texto oscuro
TEXT_LIGHT = "#ffffff"         # Texto claro

FONT_DEFAULT = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SIDEBAR = ("Segoe UI", 11, "bold")

def apply_institutional_style():
    style = ttk.Style()
    # 'clam' permite eliminar los gradientes antiguos de Windows y tener colores planos y limpios
    style.theme_use('clam')

    # --- Contenedores (Frames) ---
    style.configure('TFrame', background=BG_COLOR)
    style.configure('Sidebar.TFrame', background=PRIMARY_COLOR)
    style.configure('Content.TFrame', background=WHITE_COLOR)

    # --- Etiquetas (Labels) ---
    style.configure('TLabel', background=BG_COLOR, foreground=TEXT_DARK, font=FONT_DEFAULT)
    style.configure('Content.TLabel', background=WHITE_COLOR, foreground=TEXT_DARK, font=FONT_DEFAULT)
    style.configure('Title.TLabel', background=WHITE_COLOR, foreground=PRIMARY_COLOR, font=FONT_TITLE)
    style.configure('Sidebar.TLabel', background=PRIMARY_COLOR, foreground=TEXT_LIGHT, font=FONT_DEFAULT)

    # --- Entradas de texto (Entries) ---
    style.configure('TEntry', fieldbackground=WHITE_COLOR, foreground=TEXT_DARK, font=FONT_DEFAULT, borderwidth=1, relief='solid')

    # --- Botones estándar ---
    style.configure('TButton', background=WHITE_COLOR, foreground=TEXT_DARK, font=FONT_DEFAULT, borderwidth=1, relief='solid')
    style.map('TButton', background=[('active', '#e0e0e0')])

    # --- Botones del Sidebar (Planos, color azul, cambian en hover) ---
    style.configure('Sidebar.TButton', background=PRIMARY_COLOR, foreground=TEXT_LIGHT, font=FONT_SIDEBAR, borderwidth=0, relief='flat', focuscolor='none')
    style.map('Sidebar.TButton', background=[('active', PRIMARY_HOVER)], foreground=[('active', TEXT_LIGHT)])

    # --- Tablas (Treeview) ---
    style.configure("Treeview", background=WHITE_COLOR, foreground=TEXT_DARK, fieldbackground=WHITE_COLOR, font=FONT_DEFAULT, borderwidth=0, rowheight=30)
    style.configure("Treeview.Heading", background=PRIMARY_COLOR, foreground=TEXT_LIGHT, font=FONT_DEFAULT, borderwidth=1, relief='flat')
    style.map("Treeview", background=[('selected', PRIMARY_HOVER)], foreground=[('selected', TEXT_LIGHT)])
    style.map("Treeview.Heading", background=[('active', PRIMARY_HOVER)])
