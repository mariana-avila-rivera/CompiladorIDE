# Toolbar.py
import tkinter as tk
import os
from tkinter import ttk
from analizadores.lexico import resaltar_palabras, tokenizar_codigo


class Toolbar:
    def __init__(self, root, file_manager, editor=None, bottom_panels=None):
        self.root = root
        self.file_manager = file_manager
        self.editor = editor
        self.bottom_panels = bottom_panels
        self.toolbar_frame = None  # Añade un atributo para el frame de la toolbar
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
    
    def analizar_lexico(self):
        """Analiza el código usando el analizador léxico y muestra los errores en la pestaña correspondiente"""
        if not self.editor or not self.bottom_panels:
            return
        
        # Obtener el texto del editor
        text_area = self.editor.text_area
        
        # Ejecutar el analizador léxico y recoger errores
        errores = resaltar_palabras(text_area)
        
        # Mostrar errores en la pestaña "Errores Léxicos"
        if self.bottom_panels:
            if errores:
                errores_text = "ERRORES LÉXICOS ENCONTRADOS:\n\n" + "\n".join(errores)
            else:
                errores_text = "No se encontraron errores léxicos"
            
            # Añadir texto a la pestaña
            self.bottom_panels.add_text_to_tab("Errores Léxicos", errores_text, clear=True)
            
            # Mostrar la pestaña de errores léxicos
            left_notebook = self.bottom_panels.left_notebook
            tabs = left_notebook.tabs()
            
            # Buscar el índice de la pestaña "Errores Léxicos"
            for i, tab_id in enumerate(tabs):
                if left_notebook.tab(tab_id, "text") == "Errores Léxicos":
                    left_notebook.select(i)
                    break
                    
            # Obtener los tokens del código
            tokens = tokenizar_codigo(text_area)
            
            # Preparar el texto para mostrar en la pestaña "Léxico"
            tokens_text = "TOKENIZADO:\n\n"
            for tipo, valor, linea, columna in tokens:
                tokens_text += f"{tipo} ({linea}, {columna}): '{valor}'\n"
            
            # Añadir texto a la pestaña Léxico
            self.bottom_panels.add_text_to_tab("Léxico", tokens_text, clear=True)

    def create_toolbar(self):
        self.toolbar_frame = tk.Frame(self.root) # Asigna el Frame a self.toolbar_frame

        # Botones de compilar
        icons = {
            "Nuevo": self.resize_icon("media/icons/newFile.png"),
            "Abrir": self.resize_icon("media/icons/openFile.png"),
            "Guardar": self.resize_icon("media/icons/saveFile.png"),
            "Cerrar": self.resize_icon("media/icons/closeFile.png"),
            "Compilar": self.resize_icon("media/icons/compile.png"),
            "Debuguear": self.resize_icon("media/icons/debugg.png"),
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
            ("Lexico", self.analizar_lexico),
            ("Sintáctico", None),
            ("Semántico", None),
        ]
        for label, command in buttonsIcons:
            btn = ttk.Button(self.toolbar_frame, image=icons[label], command=command)
            if label == "Compilar":
                separator = ttk.Separator(self.toolbar_frame, orient="vertical")
                separator.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)
            btn.image = icons[label]
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X) # Empaqueta el frame aquí

        separator = ttk.Separator(self.toolbar_frame, orient="vertical")
        separator.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y)

        for label, command in buttons:
            btn = ttk.Button(self.toolbar_frame, text=label, command=command)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # No necesitas empaquetar toolbar aquí de nuevo, ya empaquetaste toolbar_frame
        # toolbar.pack(side=tk.TOP, fill=tk.X)