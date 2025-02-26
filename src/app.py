import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

arch_abierto = None


def new_file():
    global arch_abierto
    if arch_abierto or text_area.get("1.0", tk.END).strip():
        arch_abierto = None
        open_window()
    else:
        text_area.delete("1.0", tk.END)
        text_area.config(state=tk.NORMAL)
        update_line_numbers()
    text_area.yview(tk.END)  # Desplazar automáticamente al final


def open_file():
    file_path = filedialog.askopenfilename()
    global arch_abierto
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as archivo:
                contenido = archivo.read()
                arch_abierto = file_path
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as archivo:
                contenido = archivo.read()
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", contenido)
    update_line_numbers()


def save_file(event=None):
    global arch_abierto
    if not arch_abierto:
        save_file_as()
    else:
        with open(arch_abierto, "w", encoding="utf-8") as archivo:
            archivo.write(text_area.get("1.0", tk.END).strip())
            # Guardar el contenido limpiando espacios extra



def save_file_as():
    global arch_abierto
    ruta = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt"),
                   ("Todos los archivos", "*.*")]
    )
    if ruta:
        arch_abierto = ruta  # Actualizar la variable global
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(text_area.get("1.0", tk.END))


def close_file():
    global arch_abierto
    arch_abierto = None
    text_area.delete("1.0", tk.END)
    update_line_numbers()


def open_window(): # Para abrir un arch. Nuevo
    ventana = tk.Toplevel(root)
    ventana.title("Mensaje")
   
    # Tamaño de la ventana emergente
    ancho_ventana = 300
    alto_ventana = 150

    # Obtener tamaño de la pantalla
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    # Calcular coordenadas para centrar
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    # Establecer geometría de la ventana emergente
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    etiqueta = tk.Label(ventana, text="¿Salir sin guardar?",
                        font=("Arial", 12))
    etiqueta.pack(pady=20)

    botones_frame = tk.Frame(ventana)
    botones_frame.pack()

    btnG = tk.Button(botones_frame, text="Guardar",
                     command=lambda: opVentana(save_file, ventana))
    btnG.pack(side=tk.LEFT, padx=10)

    btnNG = tk.Button(botones_frame, text="No Guardar",
                      command=lambda: opVentana(close_file, ventana))
    btnNG.pack(side=tk.LEFT, padx=10)


def opVentana(funcion, ventana):
    ventana.destroy()  # Cerrar la ventana emergente
    funcion()  # Guardar o cerrar el archivo
    global arch_abierto
    arch_abierto = None  # Reiniciar la variable global
    text_area.delete("1.0", tk.END)  # Limpiar el área de texto
    text_area.config(state=tk.NORMAL)  # Asegurar que es editable
    update_line_numbers()  # Actualizar números de línea
    text_area.yview(tk.END)  # Desplazar al final automáticamente


def close_window():
    ventana = tk.Toplevel(root)
    ventana.title("Mensaje")

    # Tamaño de la ventana emergente
    ancho_ventana = 300
    alto_ventana = 150

    # Obtener tamaño de la pantalla
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    # Calcular coordenadas para centrar
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2

    # Establecer geometría de la ventana emergente
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    etiqueta = tk.Label(ventana, text="¿Salir sin guardar?",
                        font=("Arial", 12))
    etiqueta.pack(pady=20)

    botones_frame = tk.Frame(ventana)
    botones_frame.pack()

    btnG = tk.Button(botones_frame, text="Guardar",
                     command=lambda: acVentana(save_file, ventana))
    btnG.pack(side=tk.LEFT, padx=10)

    btnNG = tk.Button(botones_frame, text="No Guardar",
                      command=lambda: acVentana(close_file, ventana))
    btnNG.pack(side=tk.LEFT, padx=10)


def acVentana(funcion, ventana):
    ventana.destroy()  # Cerrar la ventana emergente
    funcion()  # Ejecutar la función correspondiente
    close_file()


def update_line_column():
    index = text_area.index(tk.INSERT)
    line = index.split(".")[0]
    column = int(index.split(".")[1]) + 1
    line_label.config(text=f"Línea: {line}")
    col_label.config(text=f"Columna: {column}")


def resize_icon(image_path, size=(18, 18)):
    try:
        icon = tk.PhotoImage(file=image_path)
        return icon.subsample(int(icon.width() / size[0]),
                              int(icon.height() / size[1]))
    except Exception as e:
        print(f"Error cargando el icono {image_path}: {e}")
        return None


root = tk.Tk()
root.title("Compilador")
root.geometry("900x600")

# Barra de menú
# Menú de archivo
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Nuevo Archivo", command=new_file)
file_menu.add_command(label="Abrir Archivo", command=open_file)
file_menu.add_command(label="Guardar Archivo", command=save_file)
file_menu.add_command(label="Guardar Archivo Como...", command=save_file_as)
file_menu.add_separator()
file_menu.add_command(label="Cerrar Archivo", command=close_window)
menubar.add_cascade(label="Archivo", menu=file_menu)

# Menu del compilador
compile_menu = tk.Menu(menubar, tearoff=0)
compile_menu.add_command(label="Lexico", command=None)
compile_menu.add_command(label="Sintáctico", command=None)
compile_menu.add_command(label="Semántico", command=None)
menubar.add_cascade(label="Compilar", menu=compile_menu)

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
    ("Cerrar", close_window),
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

# Agregar Scrollbar horizontal
h_scrollbar = tk.Scrollbar(text_panel, orient="horizontal", command=text_area.xview)

# Configurar el Text para permitir desplazamiento horizontal
text_area.config(wrap="none", xscrollcommand=h_scrollbar.set)


# Función para sincronizar el desplazamiento vertical
def sync_scroll(event):
    line_numbers_panel.yview_moveto(text_area.yview()[0])


# Función para sincronizar el desplazamiento horizontal
def sync_h_scroll(event):
    text_area.xview_moveto(h_scrollbar.get()[0])


def update_line_numbers(event=None):
    # Actualizar la numeración de líneas
    line_numbers_panel.config(state="normal")
    line_numbers_panel.delete(1.0, tk.END)

    # Obtener el número total de líneas
    line_count = int(text_area.index("end-1c").split(".")[0])

    # Generar la numeración de líneas
    line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))

    # Insertar la numeración en el widget de líneas
    line_numbers_panel.insert(1.0, line_numbers_string)
    line_numbers_panel.config(state="disabled")

# Vínculo para actualizar los números de línea cuando se modifique el texto
def update_status(event=None):
    update_line_numbers(event)
    update_line_column()
    sync_scroll(event)


# Vínculos para actualizar números de línea y línea/columna
text_area.bind("<KeyRelease>", update_status)
text_area.bind("<ButtonRelease-1>", update_status)
text_area.bind("<MouseWheel>", update_status)
text_area.bind("<Configure>", update_status)

# Vínculo para sincronizar los desplazamientos
text_area.bind("<MouseWheel>", update_status)
text_area.bind("<Up>", update_status)
text_area.bind("<Down>", update_status)
text_area.bind("<Shift-MouseWheel>", sync_h_scroll)

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
