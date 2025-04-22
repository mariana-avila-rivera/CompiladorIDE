import tkinter as tk
from tkinter import ttk


class MenuBar:
    def __init__(self, root, file_manager):
        self.root = root
        self.file_manager = file_manager
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo Archivo",
                              command=self.file_manager.new_file)
        file_menu.add_command(label="Abrir Archivo",
                              command=self.file_manager.open_file)
        file_menu.add_command(label="Guardar Archivo",
                              command=self.file_manager.save_file)
        file_menu.add_command(label="Guardar Como...",
                              command=self.file_manager.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Cerrar Archivo",
                              command=self.file_manager.close_file)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Compilar
        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="Lexico", command=None)
        compile_menu.add_command(label="Sintáctico", command=None)
        compile_menu.add_command(label="Semántico", command=None)
        menubar.add_cascade(label="Compilar", menu=compile_menu)

        self.root.config(menu=menubar)
