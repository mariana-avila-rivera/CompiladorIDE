import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

arch_abierto = None

def new_file():
    global arch_abierto
    arch_abierto = None
    text_area.delete("1.0", tk.END)
    text_area.config(state=tk.NORMAL)
    update_line_numbers()
    text_area.yview(tk.END)  # Desplazar automáticamente al final

def open_file():
    global arch_abierto
    file_path = filedialog.askopenfilename(
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    arch_abierto = file_path
    if file_path:
        with open(file_path, "r", encoding="utf-8") as archivo:
            text_area.delete("1.0", tk.END)
            text_area.insert("1.0", archivo.read())
        text_area.config(state=tk.NORMAL)
        update_line_numbers()
        text_area.yview(tk.END)  # Desplazar automáticamente al final

def save_file():
    if not arch_abierto:
        save_file_as()
    with open(arch_abierto, "w", encoding="utf-8") as archivo:
        archivo.write(text_area.get("1.0", tk.END))

def save_file_as():
    ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Todos los archivos", "*.*")]
    )
    if ruta:
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(text_area.get("1.0", tk.END))
            
def close_archive():
    global arch_abierto
    arch_abierto = None
    text_area.delete("1.0", tk.END)
    text_area.config(state=tk.DISABLED)
    update_line_numbers()
            

def update_line_column():
    index = text_area.index(tk.INSERT)
    line = index.split(".")[0]
    column = int(index.split(".")[1]) + 1
    line_label.config(text=f"Línea: {line}")
    col_label.config(text=f"Columna: {column}")
    

def close_app():
    root.quit()

def resize_icon(image_path, size=(18, 18)):
    icon = tk.PhotoImage(file=image_path)
    return icon.subsample(int(icon.width() / size[0]), int(icon.height() / size[1]))

root = tk.Tk()
root.title("Compilador")
root.geometry("900x600")

# Barra de menú
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Nuevo Archivo", command=new_file)
file_menu.add_command(label="Abrir Archivo", command=open_file)
file_menu.add_command(label="Guardar Archivo", command=save_file)
file_menu.add_command(label="Guardar Archivo Como...", command=save_file_as)
file_menu.add_separator()
file_menu.add_command(label="Cerrar", command=close_app)
menubar.add_cascade(label="Archivo", menu=file_menu)
root.config(menu=menubar)

# Barra de herramientas
toolbar = tk.Frame(root)
icons = {
    "Nuevo": resize_icon("media/icons/newFile.png"),
    "Abrir": resize_icon("media/icons/openFile.png"),
    "Guardar": resize_icon("media/icons/saveFile.png"),
    "Cerrar": resize_icon("media/icons/closeFile.png"),
    "Compilar": resize_icon("media/icons/compile.png"),
    "Debuguear": resize_icon("media/icons/debugg.png"),
}
buttonsIcons = [
    ("Nuevo", new_file),
    ("Abrir", open_file),
    ("Guardar", save_file),
    ("Cerrar", close_archive),
    ("Compilar", None),
    ("Debuguear", None),
]
buttons = [
    ("Lexico", None),
    ("Sintáctico", None),
    ("Semántico", None),
]
for label, command in buttonsIcons:
    btn = ttk.Button(toolbar, image=icons[label], command=command)
    if label == "Compilar":
        separator = ttk.Separator(toolbar, orient="vertical")
        separator.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
    btn.image = icons[label]
    btn.pack(side=tk.LEFT, padx=2, pady=2)

separator = ttk.Separator(toolbar, orient="vertical")
separator.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)

for label, command in buttons:
    btn = ttk.Button(toolbar, text=label, command=command)
    btn.pack(side=tk.LEFT, padx=2, pady=2)

toolbar.pack(side=tk.TOP, fill=tk.X)

# PanedWindow principal (vertical)
main_panel = tk.PanedWindow(root, orient=tk.VERTICAL)
main_panel.pack(fill=tk.BOTH, expand=True)

# Panel para el área de texto
text_panel = tk.Frame(main_panel)

# Agregar el Scrollbar para el conjunto
scrollbar = tk.Scrollbar(text_panel, orient="vertical")

# Crear un widget 'Text' para los números de línea, alineado a la izquierda
line_numbers_panel = tk.Text(text_panel, width=4, padx=5, bg="lightgray", bd=0, height=30, font=("Courier", 10), state="disabled", yscrollcommand=scrollbar.set)
line_numbers_panel.pack(side=tk.LEFT, fill=tk.Y)

# Área de texto (con Scrollbar)
text_area = tk.Text(text_panel, wrap=tk.WORD, undo=True, width=80, height=30, font=("Courier", 10), yscrollcommand=scrollbar.set)
text_area.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

# Configuración del scrollbar para el conjunto
scrollbar.config(command=lambda *args: [line_numbers_panel.yview(*args), text_area.yview(*args)])
scrollbar.pack(side=tk.LEFT, fill=tk.Y)

# Función para sincronizar el desplazamiento
def sync_scroll(event):
    line_numbers_panel.yview_moveto(text_area.yview()[0])

def update_line_numbers(event=None):
    # Guardar la posición actual del desplazamiento vertical
    current_yview = text_area.yview()

    # Obtén el número de líneas en el área de texto
    lines = text_area.get("1.0", "end-1c").splitlines()
    
    # Hacer que la edición de números de línea sea posible
    line_numbers_panel.config(state="normal")
    
    # Borrar solo los números de línea previos que ya no sean necesarios
    line_numbers_panel.delete("1.0", "end-1c")
    
    # Insertar los nuevos números de línea
    for i, line in enumerate(lines, 1): 
        line_numbers_panel.insert("end", f"{i}\n")
    
    # Restaurar el estado de solo lectura
    line_numbers_panel.config(state="disabled")
    
    # Restaurar la posición del desplazamiento
    line_numbers_panel.yview_moveto(text_area.yview()[0])

# Vínculo para actualizar los números de línea cuando se modifique el texto
def update_status(event=None):
    update_line_numbers()
    update_line_column()

# Vínculos para actualizar números de línea y línea/columna
text_area.bind("<KeyRelease>", update_status)
text_area.bind("<ButtonRelease-1>", update_status)

# Vínculo para sincronizar los desplazamientos
text_area.bind("<MouseWheel>", sync_scroll)
text_area.bind("<Up>", sync_scroll)
text_area.bind("<Down>", sync_scroll)


text_panel.pack(fill=tk.BOTH, expand=True)
main_panel.add(text_panel, stretch="always")

# Paneles inferiores (que no deben tapar el texto)
bottom_pane = tk.PanedWindow(main_panel, orient=tk.HORIZONTAL)
main_panel.add(bottom_pane)

# Paneles con pestañas (Errores y otros resultados)
notebook_left = ttk.Notebook(bottom_pane)
for tab_name in ["Errores Léxicos", "Errores Sintácticos", "Errores Semánticos", "Resultados"]:
    frame = tk.Frame(notebook_left)
    text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state="disabled")
    text.pack(expand=True, fill=tk.BOTH)
    notebook_left.add(frame, text=tab_name)
bottom_pane.add(notebook_left, stretch="always")

# Panel derecho con pestañas (Léxico, Sintáctico, etc.)
notebook_right = ttk.Notebook()
for tab_name in ["Léxico", "Sintáctico", "Semántico", "Hash Table", "Código Intermedio"]:
    frame = tk.Frame(notebook_right)
    text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state="disabled")
    text.pack(expand=True, fill=tk.BOTH)
    notebook_right.add(frame, text=tab_name)
bottom_pane.add(notebook_right, stretch="always")

# Panel de estado (barra inferior fija)
status_panel = tk.Frame(main_panel, relief=tk.SUNKEN, borderwidth=1)
status_panel.pack(side=tk.BOTTOM, fill=tk.X)

line_label = ttk.Label(status_panel, text="Línea: 1", width=15, anchor="w")
line_label.pack(side=tk.LEFT, padx=5, pady=5)

col_label = ttk.Label(status_panel, text="Columna: 1", width=15, anchor="w")
col_label.pack(side=tk.LEFT, padx=5, pady=5)



# Atajos de teclado
root.bind("<Control-s>", save_file)
root.bind("<Control-o>", open_file)
root.bind("<Control-Shift-s>", save_file_as)

root.mainloop()
