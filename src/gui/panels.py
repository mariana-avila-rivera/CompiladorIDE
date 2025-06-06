import tkinter as tk
from tkinter import ttk, scrolledtext
from analizadores.sintactico import TreeVisualizationWidget


class BottomPanels:
    def __init__(self, parent):
        self.parent = parent
        self.text_widgets = {}  # Diccionario para almacenar los widgets de texto
        self.tree_widget = None  # Widget para el árbol sintáctico
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
        self.add_tabs_with_special(self.right_notebook,
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
    
    def add_tabs_with_special(self, notebook, tab_names):
        """Agrega pestañas con tratamiento especial para el árbol sintáctico"""
        for name in tab_names:
            frame = tk.Frame(notebook)
            
            if name == "Sintáctico":
                # Crear widget especializado para el árbol sintáctico
                self.tree_widget = TreeVisualizationWidget(frame)
                # También agregar un widget de texto para información adicional
                info_frame = tk.Frame(frame)
                info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
                
                info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
                info_text.pack(fill=tk.X)
                info_text.insert('1.0', "Información del análisis sintáctico aparecerá aquí...")
                info_text.config(state="disabled")
                
                self.text_widgets[name + "_info"] = info_text
            else:
                # Pestaña normal con ScrolledText
                text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
                text.pack(expand=True, fill=tk.BOTH)
                self.text_widgets[name] = text
                text.config(state="disabled")
            
            notebook.add(frame, text=name)
    
    def get_text_widget(self, tab_name):
        """Obtener el widget de texto de una pestaña específica"""
        return self.text_widgets.get(tab_name)
    
    def get_tree_widget(self):
        """Obtener el widget del árbol sintáctico"""
        return self.tree_widget
    
    def add_text_to_tab(self, tab_name, text_content, clear=False):
        """Agregar texto a una pestaña específica"""
        widget = self.get_text_widget(tab_name)
        if widget:
            widget.config(state="normal")
            if clear:
                widget.delete('1.0', tk.END)
            widget.insert(tk.END, text_content + "\n")
            widget.config(state="disabled")
            # Scroll hasta el final
            widget.see(tk.END)
    
    def show_syntactic_tree(self, tree_root):
        """Mostrar el árbol sintáctico en la pestaña correspondiente"""
        if self.tree_widget:
            self.tree_widget.mostrar_arbol(tree_root)
            
            # Cambiar a la pestaña sintáctica
            tabs = self.right_notebook.tabs()
            for i, tab_id in enumerate(tabs):
                if self.right_notebook.tab(tab_id, "text") == "Sintáctico":
                    self.right_notebook.select(i)
                    break
    
    def show_syntactic_info(self, info_text):
        """Mostrar información adicional del análisis sintáctico"""
        info_widget = self.get_text_widget("Sintáctico_info")
        if info_widget:
            info_widget.config(state="normal")
            info_widget.delete('1.0', tk.END)
            info_widget.insert('1.0', info_text)
            info_widget.config(state="disabled")
    
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
