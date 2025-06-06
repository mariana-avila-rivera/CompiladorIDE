# Toolbar.py
import tkinter as tk
import os
from tkinter import ttk
from analizadores.lexico import resaltar_palabras, tokenizar_codigo
from analizadores.sintactico import AnalizadorSintactico


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

    def analizar_sintactico(self):
        """Analiza el código usando el analizador sintáctico y muestra los resultados en terminal y errores en panel"""
        if not self.editor or not self.bottom_panels:
            return
        
        # Obtener el texto del editor
        text_area = self.editor.text_area
        
        try:
            # Obtener los tokens del código usando el analizador léxico
            tokens = tokenizar_codigo(text_area)
            
            # Crear instancia del analizador sintáctico
            analizador = AnalizadorSintactico()
            
            # Inicializar el analizador (calcular primeros, siguientes y tabla LL1)
            analizador.inicializar()
            
            # Realizar el análisis sintáctico
            exito, arbol_sintactico = analizador.analizar(tokens)
            
            # Si hubo errores, crear lista de errores
            if not exito:
                errores = ["Error en el análisis sintáctico"]
            else:
                errores = []
            
            # Preparar texto para mostrar en terminal
            resultado_terminal = "ANÁLISIS SINTÁCTICO:\n"
            resultado_terminal += "=" * 50 + "\n\n"
            
            if errores:
                resultado_terminal += "ERRORES ENCONTRADOS:\n"
                for error in errores:
                    resultado_terminal += f"- {error}\n"
                resultado_terminal += "\n"
            else:
                resultado_terminal += "✓ Análisis sintáctico completado exitosamente\n\n"
            
            # Mostrar información del árbol si existe
            if arbol_sintactico:
                resultado_terminal += "ÁRBOL SINTÁCTICO GENERADO:\n"
                resultado_terminal += f"Nodo raíz: {arbol_sintactico.valor}\n"
                resultado_terminal += f"Número de hijos: {len(arbol_sintactico.hijos)}\n\n"
            
            # Mostrar en la terminal (consola)
            print(resultado_terminal)
            
            # Preparar errores para mostrar en el panel izquierdo
            if errores:
                errores_panel = "ERRORES SINTÁCTICOS ENCONTRADOS:\n\n"
                for error in errores:
                    # Extraer línea y columna del error si están disponibles
                    if "línea" in error.lower() and "columna" in error.lower():
                        errores_panel += f"Error sintáctico: {error}\n"
                    else:
                        errores_panel += f"Error sintáctico: {error}\n"
            else:
                errores_panel = "No se encontraron errores sintácticos"
            
            # Mostrar errores en la pestaña "Errores Sintácticos"
            self.bottom_panels.add_text_to_tab("Errores Sintácticos", errores_panel, clear=True)
            
            # Preparar resultado del análisis para mostrar en la pestaña "Sintáctico"
            resultado_analisis = "RESULTADO DEL ANÁLISIS SINTÁCTICO:\n\n"
            
            if errores:
                resultado_analisis += f"Estado: ERRORES ENCONTRADOS ({len(errores)} errores)\n\n"
                resultado_analisis += "Detalles de errores:\n"
                for i, error in enumerate(errores, 1):
                    resultado_analisis += f"{i}. {error}\n"
            else:
                resultado_analisis += "Estado: ANÁLISIS EXITOSO ✓\n\n"
                if arbol_sintactico:
                    resultado_analisis += "Árbol sintáctico generado correctamente\n"
                    resultado_analisis += f"Estructura del programa analizada: {arbol_sintactico.valor}\n"
            
            resultado_analisis += f"\nTokens analizados: {len(tokens)}\n"
            resultado_analisis += f"Tiempo de análisis: Completo\n"
            
            # Mostrar en la pestaña de análisis sintáctico
            self.bottom_panels.add_text_to_tab("Sintáctico", resultado_analisis, clear=True)
            
            # Mostrar la pestaña de errores sintácticos en el panel izquierdo
            left_notebook = self.bottom_panels.left_notebook
            tabs = left_notebook.tabs()
            
            # Buscar el índice de la pestaña "Errores Sintácticos"
            for i, tab_id in enumerate(tabs):
                if left_notebook.tab(tab_id, "text") == "Errores Sintácticos":
                    left_notebook.select(i)
                    break
                    
        except Exception as e:
            error_msg = f"Error durante el análisis sintáctico: {str(e)}"
            print(f"ERROR: {error_msg}")
            
            # Mostrar error en el panel
            self.bottom_panels.add_text_to_tab("Errores Sintácticos", f"ERROR CRÍTICO:\n{error_msg}", clear=True)
            self.bottom_panels.add_text_to_tab("Sintáctico", f"ERROR CRÍTICO:\n{error_msg}", clear=True)

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
            ("Sintáctico", self.analizar_sintactico),
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