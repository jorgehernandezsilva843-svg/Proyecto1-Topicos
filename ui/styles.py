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

def aplicar_tema(modo, root):
    style = ttk.Style()
    
    if modo == 'oscuro':
        bg_color = "#1e1e1e"
        fg_color = "#e0e0e0"
        sidebar_bg = "#121212"
        tree_bg = "#2d2d2d"
        card_bg = "#2a2a2a"
        title_fg = "#ffffff"
        btn_hover = "#333333"
    else:
        bg_color = "#ffffff"
        fg_color = "#333333"
        sidebar_bg = "#132c54"
        tree_bg = "#ffffff"
        card_bg = "#f4f4f4"
        title_fg = "#132c54"
        btn_hover = "#1e4480"
        
    style.configure('TFrame', background=bg_color)
    style.configure('Content.TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=fg_color)
    style.configure('Content.TLabel', background=bg_color, foreground=fg_color)
    style.configure('Title.TLabel', background=bg_color, foreground=title_fg)
    
    style.configure('Sidebar.TFrame', background=sidebar_bg)
    style.configure('Sidebar.TLabel', background=sidebar_bg, foreground="#ffffff")
    style.configure('Sidebar.TButton', background=sidebar_bg, foreground="#ffffff")
    style.map('Sidebar.TButton', background=[('active', btn_hover)])
    
    style.configure('Treeview', background=tree_bg, foreground=fg_color, fieldbackground=tree_bg)
    style.configure('Treeview.Heading', background=sidebar_bg, foreground="#ffffff")
    
    style.configure('Card.TFrame', background=card_bg, relief="groove")
    style.configure('Card.TLabel', background=card_bg, foreground=fg_color)
    style.configure('CardTitle.TLabel', background=card_bg, foreground=title_fg, font=("Segoe UI", 10, "bold"))
    style.configure('CardValue.TLabel', background=card_bg, foreground=title_fg, font=("Segoe UI", 24, "bold"))

    def recursivo(widget):
        try:
            clase = widget.winfo_class()
            nombre = str(widget).lower()
            
            if "sidebar" in nombre or getattr(widget, "es_sidebar", False):
                if clase in ('Frame', 'Label'):
                    widget.config(bg=sidebar_bg)
                    if clase == 'Label':
                        widget.config(fg="#ffffff")
            elif "card" in nombre or getattr(widget, "es_card", False):
                if clase in ('Frame', 'Label'):
                    widget.config(bg=card_bg)
                    if clase == 'Label':
                        widget.config(fg=fg_color)
            else:
                if clase in ('Frame', 'Label', 'Checkbutton', 'Canvas'):
                    if clase != 'Button':
                        widget.config(bg=bg_color)
                    if clase in ('Label', 'Checkbutton'):
                        widget.config(fg=fg_color)
        except Exception:
            pass
        
        for child in widget.winfo_children():
            recursivo(child)
            
    recursivo(root)
    try:
        root.config(bg=bg_color)
    except:
        pass
