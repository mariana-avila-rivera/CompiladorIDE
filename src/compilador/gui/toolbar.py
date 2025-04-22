import tkinter as tk
from tkinter import ttk


class Toolbar:
    def __init__(self, root, file_manager):
        self.root = root
        self.file_manager = file_manager
        self.create_toolbar()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)

        # Botones básicos (puedes expandir esto)
        new_btn = ttk.Button(toolbar, text="Nuevo",
                             command=self.file_manager.new_file)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)

        open_btn = ttk.Button(toolbar, text="Abrir",
                              command=self.file_manager.open_file)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)

        save_btn = ttk.Button(toolbar, text="Guardar",
                              command=self.file_manager.save_file)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)
