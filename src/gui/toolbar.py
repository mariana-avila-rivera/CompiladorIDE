# Toolbar.py
import tkinter as tk
import os
import sys
from tkinter import ttk
from analizadores.lexico import resaltar_palabras, tokenizar_codigo
from analizadores.sintactico import AnalizadorSintactico

from analizadores.semantico import SemanticASTBuilder            
from analizadores.semantico import SemanticAnalyzer       
from analizadores.semantico.arbol_semantico import SemanticTreeBuilder
from analizadores.codegen.pcode_generator import PCodeGenerator
from analizadores.codegen.tm_generator import TMGenerator
import subprocess
import tempfile
import threading
import queue

class Toolbar:
    def __init__(self, root, file_manager, editor=None, bottom_panels=None):
        self.root = root
        self.file_manager = file_manager
        self.editor = editor
        self.bottom_panels = bottom_panels
        self.toolbar_frame = None  # Añade un atributo para el frame de la toolbar
        self.create_toolbar()

    def get_resource_path(self, relative_path):
        """Obtiene la ruta absoluta al recurso, funcionando tanto en dev como en PyInstaller"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        return os.path.join(base_path, relative_path)

    def resize_icon(self, image_path, size=(18, 18)):
        try:
            full_path = self.get_resource_path(image_path)
            icon = tk.PhotoImage(file=full_path)
            return icon.subsample(int(icon.width() / size[0]),
                                  int(icon.height() / size[1]))
        except Exception as e:
            print(f"Error cargando el icono {image_path}: {e}")
            # Intentar ruta original por si acaso
            try:
                icon = tk.PhotoImage(file=image_path)
                return icon.subsample(int(icon.width() / size[0]),
                                      int(icon.height() / size[1]))
            except:
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
        """Fase Semántica: construye AST, analiza tipos, genera árbol semántico y muestra resultados."""
        if not self.editor or not self.bottom_panels:
            return

        text_area = self.editor.text_area
        try:
            print("\n" + "="*50)
            print("[SEMÁNTICO] Iniciando análisis semántico")
            print("="*50)
            
            # 1) Análisis Léxico: obtener tokens
            tokens = tokenizar_codigo(text_area)
            if not tokens:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "No se pudieron obtener tokens del código", clear=True)
                return
            print(f"[SEMÁNTICO] Tokens obtenidos: {len(tokens)}")

            # 2) Análisis Sintáctico: construir árbol
            analizador = AnalizadorSintactico()
            analizador.inicializar()
            exito, arbol_sintactico = analizador.analizar(tokens)

            # Verificar errores sintácticos antes de continuar
            errores_sintacticos = analizador.obtener_errores()
            if errores_sintacticos:
                msg = "No se puede continuar con el análisis semántico debido a errores sintácticos:\n\n"
                for e in errores_sintacticos:
                    msg += f"- {e['mensaje']} (Línea {e['linea']})\n"
                self.bottom_panels.add_text_to_tab("Errores Semánticos", msg, clear=True)
                
                # Seleccionar pestaña de errores sintácticos
                left_notebook = self.bottom_panels.left_notebook
                tabs = left_notebook.tabs()
                for i, tab_id in enumerate(tabs):
                    if left_notebook.tab(tab_id, "text") == "Errores Sintácticos":
                        left_notebook.select(i)
                        break
                return

            if not arbol_sintactico:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "No se pudo generar el árbol sintáctico", clear=True)
                return
            print(f"[SEMÁNTICO] Árbol sintáctico generado")

            # 3) Construir AST normalizado
            builder = SemanticASTBuilder()
            ast = builder.construir_ast(arbol_sintactico)  # ← CORRECCIÓN AQUÍ
            print(f"[SEMÁNTICO] AST construido: {ast}")

            # 4) Análisis Semántico
            sema = SemanticAnalyzer()
            _, tabla_hash, errores = sema.analyze(ast)
            print(f"[SEMÁNTICO] Análisis completado. Errores: {len(errores)}")

            # 5) Construir árbol semántico con valores evaluados Y errores
            print("[SEMÁNTICO] Construyendo árbol semántico...")
            tree_builder = SemanticTreeBuilder(sema.ts, errores)  # Pasar errores al builder
            arbol_semantico = tree_builder.construir(ast)
            print(f"[SEMÁNTICO] Árbol semántico construido")

            # 6) Mostrar árbol semántico en la pestaña Semántico
            if arbol_semantico:
                print("[SEMÁNTICO] Mostrando árbol semántico en el panel...")
                self.bottom_panels.show_semantic_tree(arbol_semantico)
            else:
                print("[SEMÁNTICO] ERROR: arbol_semantico es None")

            # 7) Mostrar Tabla Hash
            self.bottom_panels.add_text_to_tab("Hash Table", tabla_hash, clear=True)

            # 8) Mostrar Errores Semánticos
            if errores:
                errores_text = "ERRORES SEMÁNTICOS ENCONTRADOS:\n\n"
                for i, e in enumerate(errores, start=1):
                    errores_text += f"{i}.  {e['msg']} (Línea: {e['linea']}, Columna: {e['columna']})\n"
                self.bottom_panels.add_text_to_tab("Errores Semánticos", errores_text, clear=True)
            else:
                self.bottom_panels.add_text_to_tab("Errores Semánticos", "✓ No se encontraron errores semánticos", clear=True)

                # GENERACIÓN DE CÓDIGO INTERMEDIO (P-Code)
                print("[CODEGEN] Iniciando generación de Código P...")
                try:
                    generator = PCodeGenerator()
                    instructions = generator.generate(ast)
                    
                    pcode_text = "CÓDIGO P GENERADO:\n\n"
                    for i, instr in enumerate(instructions):
                        pcode_text += f"{i}\t{instr}\n"
                        
                    self.bottom_panels.add_text_to_tab("Código Intermedio", pcode_text, clear=True)
                    print(f"[CODEGEN] Código P generado: {len(instructions)} instrucciones")
                    
                    # GENERACIÓN DE CÓDIGO TM Y EJECUCIÓN
                    print("[CODEGEN] Generando código TM...")
                    tm_gen = TMGenerator()
                    
                    # Usar directorio temporal del sistema
                    temp_dir = tempfile.gettempdir()
                    temp_tm_path = os.path.join(temp_dir, "CompiladorIDE_output.tm")
                    
                    tm_gen.generate(instructions, temp_tm_path)
                    print(f"[CODEGEN] Archivo TM generado en: {temp_tm_path}")
                    
                    # Ejecutar TMVS CLI
                    # Asumimos que el ejecutable de tmvs está compilado y empaquetado
                    
                    print(f"[EXEC] Ejecutando TMVS con: {temp_tm_path}")
                    
                    # Ejecutar integrado en la GUI
                    self.run_tmvs(temp_tm_path)

                except Exception as e:
                    print(f"[CODEGEN] Error: {e}")
                    import traceback
                    traceback.print_exc()
                    self.bottom_panels.add_text_to_tab("Código Intermedio", f"Error generando código: {e}", clear=True)

            # 9) Mostrar Estado del Análisis
            info = "ANÁLISIS SEMÁNTICO COMPLETADO\n\n"
            info += f"Estado: {'EXITOSO' if not errores else 'CON ERRORES'}\n"
            info += f"Tokens procesados: {len(tokens)}\n"
            info += f"Errores encontrados: {len(errores)}\n"
            if not errores:
                info += "\n✓ Análisis semántico exitoso"
                info += "\n✓ Árbol semántico generado con valores evaluados"
            else:
                info += f"\n⚠ Se encontraron {len(errores)} errores semánticos"
            
            if hasattr(self.bottom_panels, 'show_semantic_info'):
                self.bottom_panels.show_semantic_info(info)

            # 10) Mostrar las pestañas relevantes
            if errores:
                left_notebook = self.bottom_panels.left_notebook
                tabs = left_notebook.tabs()
                for i, tab_id in enumerate(tabs):
                    if left_notebook.tab(tab_id, "text") == "Errores Semánticos":
                        left_notebook.select(i)
                        break
            else:
                # Si no hay errores, mostrar la pestaña del árbol semántico
                right_notebook = self.bottom_panels.right_notebook
                tabs = right_notebook.tabs()
                for i, tab_id in enumerate(tabs):
                    if right_notebook.tab(tab_id, "text") == "Semántico":
                        right_notebook.select(i)
                        break

            print("="*50)
            print("[SEMÁNTICO] Análisis semántico finalizado")
            print("="*50 + "\n")

        except Exception as e:
            error_msg = f"Error durante el análisis semántico: {str(e)}"
            print(f"[SEMÁNTICO] ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
            self.bottom_panels.add_text_to_tab("Errores Semánticos", error_msg, clear=True)

    def get_tmvs_executable_path(self):
        """Retorna la ruta al ejecutable de la TM"""
        if getattr(sys, 'frozen', False):
            # Si estamos corriendo como ejecutable (PyInstaller)
            # El ejecutable estará en la carpeta temporal _MEIPASS/bin
            base_path = sys._MEIPASS
            exe_path = os.path.join(base_path, 'bin', 'tmvs-cli.exe')
        else:
            # Si estamos corriendo desde código fuente
            # El ejecutable está en src/bin/tmvs-cli.exe
            # self es Toolbar, está en src/gui/toolbar.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Subir a src/ y luego a bin/
            exe_path = os.path.join(current_dir, '..', 'bin', 'tmvs-cli.exe')
        
        return os.path.abspath(exe_path)

    def run_tmvs(self, tm_path, tmvs_root=None):
        # Matar proceso anterior si existe
        if hasattr(self, 'process') and self.process:
            try:
                if self.process.poll() is None: # Si sigue corriendo
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
            except Exception as e:
                print(f"Error matando proceso anterior: {e}")
            self.process = None

        # Limpiar pestaña de resultados
        self.bottom_panels.add_text_to_tab("Resultados", "", clear=True)
        
        # Seleccionar pestaña de resultados
        left_notebook = self.bottom_panels.left_notebook
        tabs = left_notebook.tabs()
        for i, tab_id in enumerate(tabs):
            if left_notebook.tab(tab_id, "text") == "Resultados":
                left_notebook.select(i)
                break

        tm_exe = self.get_tmvs_executable_path()
        print(f"[EXEC] Buscando TM en: {tm_exe}")

        if not os.path.exists(tm_exe):
             self.bottom_panels.add_text_to_tab("Resultados", f"Error: No se encontró el ejecutable de la TM en: {tm_exe}\nPor favor asegúrese de que 'src/bin/tmvs-cli.exe' exista.", clear=False)
             return

        # Comando de ejecución
        cmd = [tm_exe, tm_path, "10000"]
        
        try:
            # Iniciar proceso
            self.process = subprocess.Popen(
                cmd,
                # cwd=tmvs_root, # No es necesario cambiar de directorio
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Asegurar que la entrada inicie deshabilitada
            self.disable_input()

            # Iniciar hilo de lectura
            threading.Thread(target=self.read_output, args=(self.process,), daemon=True).start()
            
        except Exception as e:
            self.bottom_panels.add_text_to_tab("Resultados", f"Error al iniciar proceso: {e}\n", clear=False)

    def read_output(self, process):
        buffer = ""
        while True:
            char = process.stdout.read(1)
            if not char:
                if process.poll() is not None:
                    break
                continue
            
            self.root.after(0, self.update_results, char)
            
            # Detectar prompts para habilitar input
            buffer += char
            if buffer.endswith("\n"):
                buffer = ""
            elif buffer.endswith(": ") or buffer.endswith(" = "):
                self.root.after(0, self.enable_input)
                buffer = "" # Reset buffer after detection to avoid repeated triggers
        
        # Leer stderr si hay algo
        err = process.stderr.read()
        if err:
            self.root.after(0, self.update_results, f"STDERR: {err}")
            
        self.root.after(0, self.disable_input)

    def enable_input(self):
        if hasattr(self.bottom_panels, 'results_entry'):
            self.bottom_panels.results_entry.config(state="normal", bg="white")
            self.bottom_panels.results_entry.bind("<Return>", self.send_input)
            self.bottom_panels.results_entry.focus()

    def update_results(self, text):
        self.bottom_panels.add_text_to_tab("Resultados", text, clear=False, auto_newline=False)

    def send_input(self, event):
        if not hasattr(self, 'process') or self.process.poll() is not None:
            return
            
        entry = self.bottom_panels.results_entry
        text = entry.get()
        entry.delete(0, tk.END)
        
        # Mostrar lo que escribió el usuario
        self.update_results(f"{text}\n")
        
        # Enviar al proceso
        try:
            self.process.stdin.write(text + "\n")
            self.process.stdin.flush()
            # Deshabilitar input hasta el próximo prompt
            self.disable_input()
        except Exception as e:
            self.update_results(f"Error enviando input: {e}\n")

    def disable_input(self):
        if hasattr(self.bottom_panels, 'results_entry'):
            self.bottom_panels.results_entry.config(state="disabled", bg="#f0f0f0")
            self.bottom_panels.results_entry.unbind("<Return>")

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