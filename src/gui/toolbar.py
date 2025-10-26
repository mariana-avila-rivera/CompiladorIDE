# Toolbar.py
import tkinter as tk
import os
from tkinter import ttk
from analizadores.lexico import resaltar_palabras, tokenizar_codigo
from analizadores.sintactico import AnalizadorSintactico

from analizadores.semantico import SemanticASTBuilder            
from analizadores.semantico import SemanticAnalyzer       

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
        """Analiza el código usando el analizador sintáctico mejorado y muestra los resultados"""
        if not self.editor or not self.bottom_panels:
            return
        
        # Obtener el texto del editor
        text_area = self.editor.text_area
        
        try:
            # Obtener los tokens del código usando el analizador léxico
            tokens = tokenizar_codigo(text_area)
            
            if not tokens:
                self.bottom_panels.add_text_to_tab("Errores Sintácticos", "No se pudieron obtener tokens del código", clear=True)
                return
            
            # Crear instancia del analizador sintáctico
            analizador = AnalizadorSintactico()
            
            # Inicializar el analizador (calcular primeros, siguientes y tabla LL1)
            analizador.inicializar()
            
            # Realizar el análisis sintáctico
            exito, arbol_sintactico = analizador.analizar(tokens)
            
            # Obtener errores del analizador
            errores = analizador.obtener_errores()
            
            # Mostrar errores en el panel izquierdo
            if errores:
                errores_panel = "ERRORES SINTÁCTICOS ENCONTRADOS:\n\n"
                for i, error in enumerate(errores, 1):
                    errores_panel += f"{i}. {error['tipo']}: {error['mensaje']}"
                    if error['linea'] > 0:
                        errores_panel += f" (Línea: {error['linea']}, Columna: {error['columna']})"
                    errores_panel += "\n"
            else:
                errores_panel = "✓ No se encontraron errores sintácticos"
            
            # Mostrar errores en la pestaña "Errores Sintácticos"
            self.bottom_panels.add_text_to_tab("Errores Sintácticos", errores_panel, clear=True)
            
            # Mostrar errores en el panel izquierdo
            left_notebook = self.bottom_panels.left_notebook
            tabs = left_notebook.tabs()
            for i, tab_id in enumerate(tabs):
                if left_notebook.tab(tab_id, "text") == "Errores Sintácticos":
                    left_notebook.select(i)
                    break
            
            # Mostrar el árbol sintáctico en el panel derecho
            if arbol_sintactico:
                # Mostrar el árbol en el widget especializado
                self.bottom_panels.show_syntactic_tree(arbol_sintactico)
                
                # Preparar información adicional
                info_text = f"ANÁLISIS SINTÁCTICO COMPLETADO\n\n"
                info_text += f"Estado: {'EXITOSO' if exito and not errores else 'CON ERRORES'}\n"
                info_text += f"Tokens procesados: {len(tokens)}\n"
                info_text += f"Errores encontrados: {len(errores)}\n"
                if exito and not errores:
                    info_text += "✓ Árbol sintáctico generado correctamente"
                else:
                    info_text += "⚠ Árbol sintáctico generado con errores"
                
                # Mostrar información adicional
                self.bottom_panels.show_syntactic_info(info_text)
            else:
                # Si no hay árbol, mostrar mensaje
                self.bottom_panels.get_tree_widget().mostrar_mensaje("No se pudo generar el árbol sintáctico")
                
                info_text = f"ANÁLISIS SINTÁCTICO FALLIDO\n\n"
                info_text += f"Tokens procesados: {len(tokens)}\n"
                info_text += f"Errores encontrados: {len(errores)}\n"
                info_text += "✗ No se pudo generar el árbol sintáctico"
                
                self.bottom_panels.show_syntactic_info(info_text)
            
            # Información en consola
            print(f"\nAnálisis sintáctico completado:")
            print(f"- Tokens: {len(tokens)}")
            print(f"- Errores: {len(errores)}")
            print(f"- Árbol generado: {'Sí' if arbol_sintactico else 'No'}")
            
        except Exception as e:
            error_msg = f"Error crítico durante el análisis sintáctico: {str(e)}"
            print(f"ERROR: {error_msg}")
            
            # Mostrar error en los paneles
            self.bottom_panels.add_text_to_tab("Errores Sintácticos", f"ERROR CRÍTICO:\n{error_msg}", clear=True)
            if self.bottom_panels.get_tree_widget():
                self.bottom_panels.get_tree_widget().mostrar_mensaje("Error crítico en el análisis")
            
            # Mostrar información de error
            info_text = f"ERROR CRÍTICO EN EL ANÁLISIS\n\n{error_msg}"
            self.bottom_panels.show_syntactic_info(info_text)

    def analizar_semantico(self):
        """Fase Semántica: construye AST, analiza tipos y muestra resultados."""
        if not self.editor or not self.bottom_panels:
            return

        text_area = self.editor.text_area
        try:
            # 1) Análisis Léxico: obtener tokens
            tokens = tokenizar_codigo(text_area)
            if not tokens:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "No se pudieron obtener tokens del código", clear=True)
                return

            # 2) Análisis Sintáctico: construir árbol
            analizador = AnalizadorSintactico()
            analizador.inicializar()
            exito, arbol_sintactico = analizador.analizar(tokens)

            if not arbol_sintactico:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "No se pudo generar el árbol sintáctico", clear=True)
                return

            # 3) Construir AST normalizado
            builder = SemanticASTBuilder()
            ast = builder.construir_ast(arbol_sintactico)

            # 4) Análisis Semántico
            sema = SemanticAnalyzer()
            _, tabla_hash, errores = sema.analyze(ast)

            # 5) Mostrar Tabla Hash
            self.bottom_panels.add_text_to_tab("Hash Table", tabla_hash, clear=True)

            # 6) Mostrar Errores Semánticos
            if errores:
                errores_text = "ERRORES SEMÁNTICOS ENCONTRADOS:\n\n"
                for error in errores:
                    errores_text += f"• {error}\n"
                self.bottom_panels.add_text_to_tab("Errores Semánticos", errores_text, clear=True)
            else:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "✓ No se encontraron errores semánticos", clear=True)

            # 7) Mostrar Estado del Análisis
            info = "ANÁLISIS SEMÁNTICO COMPLETADO\n\n"
            info += f"Estado: {'EXITOSO' if not errores else 'CON ERRORES'}\n"
            info += f"Tokens procesados: {len(tokens)}\n"
            info += f"Errores encontrados: {len(errores)}\n"
            if not errores:
                info += "\n✓ Análisis semántico exitoso"
            else:
                info += f"\n⚠ Se encontraron {len(errores)} errores semánticos"
            self.bottom_panels.add_text_to_tab("Semántico", info, clear=True)

            # 8) Mostrar las pestañas relevantes
            if errores:
                left_notebook = self.bottom_panels.left_notebook
                tabs = left_notebook.tabs()
                for i, tab_id in enumerate(tabs):
                    if left_notebook.tab(tab_id, "text") == "Errores Semánticos":
                        left_notebook.select(i)
                        break

            # Cambiar a la pestaña de la tabla hash
            right_notebook = self.bottom_panels.right_notebook
            tabs = right_notebook.tabs()
            for i, tab_id in enumerate(tabs):
                if right_notebook.tab(tab_id, "text") == "Hash Table":
                    right_notebook.select(i)
                    break

        except Exception as e:
            error_msg = f"Error durante el análisis semántico: {str(e)}"
            print(f"[Semántico] Error: {e}")
            self.bottom_panels.add_text_to_tab("Errores Semánticos", error_msg, clear=True)
            self.bottom_panels.add_text_to_tab("Semántico", f"ERROR: {error_msg}", clear=True)

        text_area = self.editor.text_area
        try:
            # 1) LEX + SINT
            tokens = tokenizar_codigo(text_area)
            if not tokens:
                print("[Semántico] No hay tokens")
                return

            analizador = AnalizadorSintactico()
            analizador.inicializar()
            exito, arbol_sintactico = analizador.analizar(tokens)

            if not arbol_sintactico:
                print("[Semántico] No se generó árbol sintáctico")
                return

            # 2) Construir AST
            builder = SemanticASTBuilder()
            ast = builder.construir_ast(arbol_sintactico)

            # 3) Semántico: construir TS y mostrar resultados
            sema = SemanticAnalyzer()
            mensaje, tabla_hash, errores = sema.analyze(ast)

            # Mostrar la tabla hash en su panel correspondiente
            text_widget = self.bottom_panels.get_text_widget("Hash Table")
            if text_widget:
                text_widget.config(state="normal")
                text_widget.delete('1.0', tk.END)
                
                # Configurar la fuente para la tabla
                text_widget.tag_configure("table_header", font=("Courier", 10, "bold"))
                text_widget.tag_configure("table_content", font=("Courier", 10))
                
                # Insertar el contenido
                lines = tabla_hash.split('\n')
                for i, line in enumerate(lines):
                    if i < 2:  # Encabezado y línea divisoria
                        text_widget.insert(tk.END, line + "\n", "table_header")
                    else:
                        text_widget.insert(tk.END, line + "\n", "table_content")
                text_widget.config(state="disabled")
                text_widget.see('1.0')

            # Mostrar errores en el panel de errores semánticos
            if errores:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", errores, clear=True)
            else:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "No se encontraron errores semánticos", clear=True)

            # Mostrar estado en el panel semántico
            info = "ANÁLISIS SEMÁNTICO COMPLETADO\n\n"
            info += f"Estado: {'EXITOSO' if not errores else 'CON ERRORES'}\n"
            info += f"Errores semánticos: {len(errores)}\n"
            self.bottom_panels.add_text_to_tab("Semántico", info, clear=True)

        except Exception as e:
            print(f"[Semántico] Error: {e}")
            self.bottom_panels.add_text_to_tab("Semántico", f"ERROR: {e}", clear=True)

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
            ("Semántico", self.analizar_semantico),
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