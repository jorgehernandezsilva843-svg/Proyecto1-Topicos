import os

VIEWS = ["alumnos_view.py", "materias_view.py", "calificaciones_view.py", "reportes_view.py"]
BASE_DIR = r"C:\Users\Administrador\Desktop\Fund. & Simulación\Proyecto1 Topicos\ui"

for v in VIEWS:
    path = os.path.join(BASE_DIR, v)
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Cambiar herencia de Toplevel (ventana separada) a Frame (para poder incrustarlos)
    content = content.replace("(tk.Toplevel):", "(tk.Frame):")
    
    # Remover configuraciones que son exclusivas de Toplevel
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if "self.title(" in line or "self.geometry(" in line or "self.grab_set()" in line or "self.focus()" in line or "self.configure(bg=BG_COLOR)" in line:
            continue
        new_lines.append(line)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
print("Vistas adaptadas para ser incrustadas en el sidebar correctamente.")
