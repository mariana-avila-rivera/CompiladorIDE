import tkinter as tk
from tkinter import filedialog, messagebox

arch_abierto = None


# Función para abrir un archivo
def abrir_archivo():
    global arch_abierto
    ruta = filedialog.askopenfilename(
        filetypes=[
            ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")
        ])
    arch_abierto = ruta
    if ruta:
        with open(ruta, "r", encoding="utf-8") as archivo:
            # Borra el contenido actual
            texto.delete("1.0", tk.END)
            # Inserta el contenido del archivo en el área de texto
            texto.insert("1.0", archivo.read())


# Función para guardar un archivo:
# sobreescribir el archivo previamente seleccionado
# El argumento event es para atajos de teclado
#   (Puede o  no recibir evento de teclado)
def guardar_archivo(event=None):
    if not arch_abierto:
        guardar_archivo_como()
    with open(arch_abierto, "w", encoding="utf-8") as archivo:
        # Guarda el contenido del área de texto en el archivo
        archivo.write(texto.get("1.0", tk.END))


# Función para guardar un archivo y abrir el explorador de archivos
def guardar_archivo_como(event=None):
    ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                        ("Archivos de texto", "*.txt"),
                        ("Todos los archivos", "*.*")
            ])
    if ruta:
        with open(ruta, "w", encoding="utf-8") as archivo:
            # Guarda el contenido del área de texto en el archivo
            archivo.write(texto.get("1.0", tk.END))


# Crear la ventana principal
root = tk.Tk()
root.title("Editor de Texto")
root.geometry("600x400")

# Crear un menú
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

archivo_menu = tk.Menu(menu_bar, tearoff=0)
archivo_menu.add_command(label="Abrir", command=abrir_archivo)
archivo_menu.add_command(label="Guardar", command=guardar_archivo)
archivo_menu.add_command(label="Guardar como", command=guardar_archivo_como)
archivo_menu.add_separator()
archivo_menu.add_command(label="Salir", command=root.quit)
menu_bar.add_cascade(label="Archivo", menu=archivo_menu)


# Crear el área de texto con scroll
frame_texto = tk.Frame(root)
frame_texto.pack(fill=tk.BOTH, expand=True)

scroll = tk.Scrollbar(frame_texto)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

texto = tk.Text(frame_texto, wrap="word", yscrollcommand=scroll.set)
texto.pack(fill=tk.BOTH, expand=True)
scroll.config(command=texto.yview)

# 🏆 Atajos de teclado
root.bind("<Control-s>", guardar_archivo)  # Ctrl + S para guardar
root.bind("<Control-o>", abrir_archivo)    # Ctrl + O para abrir
# Ctrl + Shift + S para "Guardar como"
root.bind("<Control-Shift-s>", guardar_archivo_como)

# Ejecutar la aplicación
root.mainloop()
