import tkinter as tk
from tkinter import filedialog


class FileManager:
    def __init__(self, parent):
        self.current_file = None
        self.editor = None
        self.parent = parent
        self.arch_abierto = None

    def set_editor(self, editor):
        self.editor = editor

    def new_file(self):
        if self.arch_abierto or self.editor.text_area.get("1.0",
                                                          tk.END).strip():
            self.arch_abierto = None
            self.close_window("open")
        else:
            self.editor.text_area.delete("1.0", tk.END)
            self.editor.text_area.config(state=tk.NORMAL)
            self.editor.update_after_realize()
        self.editor.text_area.yview(tk.END)  # Desplazar al final

    def open_file(self):
        if self.arch_abierto or self.editor.text_area.get("1.0",
                                                          tk.END).strip():
            self.arch_abierto = None
            self.close_window("open")
        else:
            file_path = filedialog.askopenfilename()
            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as archivo:
                        contenido = archivo.read()
                        self.arch_abierto = file_path
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="latin-1") as archivo:
                        contenido = archivo.read()
                self.editor.text_area.delete("1.0", tk.END)
                self.editor.text_area.insert("1.0", contenido)
        self.editor.update_after_realize()  # Actualizar nums de línea

    def save_file(self):
        if not self.arch_abierto:
            self.save_file_as()
        else:
            with open(self.arch_abierto, "w",
                      encoding="utf-8") as archivo:
                archivo.write(self.editor.text_area.get("1.0", tk.END).strip())
        self.editor.update_after_realize()  # Actualizar los números de línea

    def save_file_as(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Todos los archivos", "*.*")]
        )
        if ruta:
            self.arch_abierto = ruta  # Actualizar la variable global
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(self.editor.text_area.get("1.0", tk.END))

    def close_file(self):
        self.arch_abierto = None
        self.editor.text_area.delete("1.0", tk.END)
        self.editor.update_after_realize()

# Función para mostrar un mensaje de advertencia al cerrar la ventana
    def close_window(self, tipo=None):
        # tipo= open/close
        ventana = tk.Toplevel(self.parent)
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

        if tipo == "open":
            btnG = tk.Button(botones_frame, text="Guardar",
                             command=lambda:
                                 self.opVentana(self.save_file, ventana))

            btnNG = tk.Button(botones_frame, text="No Guardar",
                              command=lambda:
                                  self.opVentana(self.close_file, ventana))
        else:
            # Es de tipo close
            btnG = tk.Button(botones_frame, text="Guardar",
                             command=lambda:
                                 self.acVentana(self.save_file, ventana))

            btnNG = tk.Button(botones_frame, text="No Guardar",
                              command=lambda:
                                  self.acVentana(self.close_file, ventana))

        btnG.pack(side=tk.LEFT, padx=10)
        btnNG.pack(side=tk.LEFT, padx=10)

    def acVentana(self, funcion, ventana):
        ventana.destroy()  # Cerrar la ventana emergente
        funcion()  # Ejecutar la función correspondiente
        self.close_file()

    def opVentana(self, funcion, ventana):
        ventana.destroy()  # Cerrar la ventana emergente
        funcion()  # Guardar o cerrar el archivo
        self.arch_abierto = None  # Reiniciar la variable global
        self.editor.text_area.delete("1.0", tk.END)  # Limpiar el área de texto
        self.editor.text_area.config(state=tk.NORMAL)  # Asegura ser editable
        self.editor.text_area.yview(tk.END)  # Desplazar al final
        self.open_file()

