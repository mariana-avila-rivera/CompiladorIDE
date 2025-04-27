import tkinter as tk
import os
from tkinter import ttk


class Toolbar:
    def __init__(self, root, file_manager):
        self.root = root
        self.file_manager = file_manager
        self.create_toolbar()

    def resize_icon(self, image_path, size=(18, 18)):
        try:
            icon = tk.PhotoImage(file=image_path)
            return icon.subsample(int(icon.width() / size[0]),
                                  int(icon.height() / size[1]))
        except Exception as e:
            print(f"Error cargando el icono {image_path}: {e}")
            print("Directorio actual:", os.getcwd())
            return None

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)

        # Botones de compilar
        icons = {
            "Nuevo": self.resize_icon("../media/icons/newFile.png"),
            "Abrir": self.resize_icon("../media/icons/openFile.png"),
            "Guardar": self.resize_icon("../media/icons/saveFile.png"),
            "Cerrar": self.resize_icon("../media/icons/closeFile.png"),
            "Compilar": self.resize_icon("../media/icons/compile.png"),
            "Debuguear": self.resize_icon("../media/icons/debugg.png"),
        }
        buttonsIcons = [
            ("Nuevo", self.file_manager.new_file),
            ("Abrir", self.file_manager.open_file),
            ("Guardar", self.file_manager.save_file),
            ("Cerrar", self.file_manager.close_window),
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

        toolbar.pack(side=tk.TOP, fill=tk.X)

        separator = ttk.Separator(toolbar, orient="vertical")
        separator.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)

        for label, command in buttons:
            btn = ttk.Button(toolbar, text=label, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)
