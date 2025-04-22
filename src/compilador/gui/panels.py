import tkinter as tk
from tkinter import ttk, scrolledtext


class BottomPanels:
    def __init__(self, parent):
        self.parent = parent
        self.create_panels()

    def create_panels(self):
        # Panel principal
        self.main_panel = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL)

        # Panel izquierdo (Errores)
        self.left_notebook = ttk.Notebook(self.main_panel)
        self.add_tabs(self.left_notebook,
                      ["Errores Léxicos",
                       "Errores Sintácticos",
                       "Errores Semánticos",
                       "Resultados"])

        # Panel derecho (Análisis)
        self.right_notebook = ttk.Notebook(self.main_panel)
        self.add_tabs(self.right_notebook,
                      ["Léxico",
                       "Sintáctico",
                       "Semántico",
                       "Hash Table",
                       "Código Intermedio"])

        # Añadir al panel principal
        self.main_panel.add(self.left_notebook)
        self.main_panel.add(self.right_notebook)
        self.main_panel.pack(fill=tk.BOTH, expand=True)

    def add_tabs(self, notebook, tab_names):
        for name in tab_names:
            frame = tk.Frame(notebook)
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text.pack(expand=True, fill=tk.BOTH)
            notebook.add(frame, text=name)
