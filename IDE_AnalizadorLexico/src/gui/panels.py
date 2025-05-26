import tkinter as tk
from tkinter import ttk, scrolledtext


class BottomPanels:
    def __init__(self, parent):
        self.parent = parent
        self.text_widgets = {}  # Diccionario para almacenar los widgets de texto
        self.create_panels()

    def create_panels(self):
        # Panel principal
        self.main_panel = tk.PanedWindow(self.parent, orient=tk.HORIZONTAL) # Usar self.parent
        self.main_panel.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo (Errores)
        self.left_notebook = ttk.Notebook(self.main_panel) # Usar self.main_panel (el PanedWindow interno)
        self.add_tabs(self.left_notebook,
                         ["Errores Léxicos",
                          "Errores Sintácticos",
                          "Errores Semánticos",
                          "Resultados"])

        # Panel derecho (Análisis)
        self.right_notebook = ttk.Notebook(self.main_panel) # Usar self.main_panel
        self.add_tabs(self.right_notebook,
                          ["Léxico",
                           "Sintáctico",
                           "Semántico",
                           "Hash Table",
                           "Código Intermedio"])

        # Añadir al panel principal
        self.main_panel.add(self.left_notebook)
        self.main_panel.add(self.right_notebook)
        # self.main_panel.pack(fill=tk.BOTH, expand=True) # Ya se empaqueta al crearse

    def add_tabs(self, notebook, tab_names):
        for name in tab_names:
            frame = tk.Frame(notebook)
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
            text.pack(expand=True, fill=tk.BOTH)
            notebook.add(frame, text=name)
            # Guardar referencia al widget de texto
            self.text_widgets[name] = text
            # Configurar el widget como solo lectura
            text.config(state="disabled")
    
    def get_text_widget(self, tab_name):
        """Obtener el widget de texto de una pestaña específica"""
        return self.text_widgets.get(tab_name)
    
    def add_text_to_tab(self, tab_name, text, clear=False):
        """Añadir texto a una pestaña específica"""
        text_widget = self.get_text_widget(tab_name)
        if text_widget:
            # Habilitar temporalmente para poder modificar
            text_widget.config(state="normal")
            if clear:
                text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, text)
            # Desplazar automáticamente al inicio
            text_widget.see("1.0")
            # Volver a deshabilitar para solo lectura
            text_widget.config(state="disabled")
