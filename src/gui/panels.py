import tkinter as tk
from tkinter import ttk, scrolledtext
from analizadores.sintactico import TreeVisualizationWidget, ASTBuilder
from analizadores.semantico.arbol_semantico import SemanticTreeWidget

class BottomPanels:
    def __init__(self, parent):
        self.parent = parent
        self.text_widgets = {}
        self.tree_widget = None
        self.semantic_tree_widget = None  # Widget para árbol semántico
        self.ast_builder = ASTBuilder()
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
        """Agrega pestañas con tratamiento especial para árboles"""
        for name in tab_names:
            frame = tk.Frame(notebook)
            
            if name == "Sintáctico":
                # Widget especializado para el árbol sintáctico
                self.tree_widget = TreeVisualizationWidget(frame)
                # Widget de texto para información adicional
                info_frame = tk.Frame(frame)
                info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
                
                info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
                info_text.pack(fill=tk.X)
                info_text.insert('1.0', "Información del análisis sintáctico aparecerá aquí...")
                info_text.config(state="disabled")
                
                self.text_widgets[name + "_info"] = info_text
            
            elif name == "Semántico":
                print(f"[BottomPanels] Creando pestaña Semántico")
                
                # Widget de texto para información adicional (PRIMERO)
                info_frame = tk.Frame(frame)
                info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
                
                info_text = tk.Text(info_frame, height=4, wrap=tk.WORD)
                info_text.pack(fill=tk.X)
                info_text.insert('1.0', "Información del análisis semántico aparecerá aquí...")
                info_text.config(state="disabled")
                
                self.text_widgets[name + "_info"] = info_text
                
                # Widget especializado para el árbol semántico (DESPUÉS, para que ocupe el resto)
                self.semantic_tree_widget = SemanticTreeWidget(frame)
                self.semantic_tree_widget.pack(expand=True, fill=tk.BOTH)
                
                print(f"[BottomPanels] SemanticTreeWidget creado y empaquetado")
            
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
    
    def get_semantic_tree_widget(self):
        """Obtener el widget del árbol semántico"""
        return self.semantic_tree_widget
    
    def show_syntactic_tree(self, tree_root):
        """Mostrar el árbol sintáctico en la pestaña correspondiente"""
        if self.tree_widget and tree_root:
            # AQUÍ ESTÁ LA CLAVE: Procesar el árbol sintáctico crudo con el AST Builder
            try:
                print("Procesando árbol sintáctico crudo...")
                print(f"Árbol recibido: {tree_root.valor if hasattr(tree_root, 'valor') else tree_root}")
                
                # Construir AST limpio a partir del árbol sintáctico crudo
                ast_procesado = self.ast_builder.construir_ast(tree_root)
                
                if ast_procesado:
                    print("AST procesado exitosamente")
                    # Mostrar el AST procesado en lugar del árbol crudo
                    self.tree_widget.mostrar_arbol(ast_procesado)
                    
                    # Mostrar información adicional
                    info_text = "Análisis sintáctico completado exitosamente.\nÁrbol procesado y filtrado."
                    self.show_syntactic_info(info_text)
                else:
                    print("Error: AST procesado es None")
                    # Si falla el procesamiento, mostrar el árbol original
                    self.tree_widget.mostrar_arbol(tree_root)
                    self.show_syntactic_info("Árbol sintáctico mostrado sin procesar.")
                    
            except Exception as e:
                print(f"Error procesando AST: {e}")
                # En caso de error, mostrar el árbol original
                self.tree_widget.mostrar_arbol(tree_root)
                self.show_syntactic_info(f"Error procesando AST: {e}")
            
            # Cambiar a la pestaña sintáctica
            tabs = self.right_notebook.tabs()
            for i, tab_id in enumerate(tabs):
                if self.right_notebook.tab(tab_id, "text") == "Sintáctico":
                    self.right_notebook.select(i)
                    break
    
    def show_semantic_tree(self, tree_root):
        """Mostrar el árbol semántico en la pestaña correspondiente"""
        print(f"[BottomPanels] show_semantic_tree llamado con: {tree_root}")
        
        if self.semantic_tree_widget and tree_root:
            try:
                print("[BottomPanels] Mostrando árbol semántico...")
                print(f"[BottomPanels] Tipo de nodo raíz: {type(tree_root)}")
                print(f"[BottomPanels] Atributos del nodo: tipo={getattr(tree_root, 'tipo', 'N/A')}, valor={getattr(tree_root, 'valor', 'N/A')}")
                
                # Mostrar el árbol en el widget
                self.semantic_tree_widget.mostrar_arbol(tree_root)
                
                # Cambiar a la pestaña semántica
                tabs = self.right_notebook.tabs()
                for i, tab_id in enumerate(tabs):
                    if self.right_notebook.tab(tab_id, "text") == "Semántico":
                        self.right_notebook.select(i)
                        print(f"[BottomPanels] Cambiado a pestaña Semántico (índice {i})")
                        break
                
                print("[BottomPanels] Árbol semántico mostrado exitosamente")
                
            except Exception as e:
                print(f"[BottomPanels] Error mostrando árbol semántico: {e}")
                import traceback
                traceback.print_exc()
        else:
            if not self.semantic_tree_widget:
                print("[BottomPanels] ERROR: semantic_tree_widget es None")
            if not tree_root:
                print("[BottomPanels] ERROR: tree_root es None")
    
    def show_syntactic_info(self, info_text):
        """Mostrar información adicional del análisis sintáctico"""
        info_widget = self.get_text_widget("Sintáctico_info")
        if info_widget:
            info_widget.config(state="normal")
            info_widget.delete('1.0', tk.END)
            info_widget.insert('1.0', info_text)
            info_widget.config(state="disabled")
    
    def show_semantic_info(self, info_text):
        """Mostrar información adicional del análisis semántico"""
        info_widget = self.get_text_widget("Semántico_info")
        if info_widget:
            info_widget.config(state="normal")
            info_widget.delete('1.0', tk.END)
            info_widget.insert('1.0', info_text)
            info_widget.config(state="disabled")
    
    def add_text_to_tab(self, tab_name, text, clear=False):
        widget = self.get_text_widget(tab_name)
        if widget:
            widget.config(state="normal")
            if clear:
                widget.delete("1.0", tk.END)
            # Asegura string + salto de línea final
            s = text if isinstance(text, str) else str(text)
            if not s.endswith("\n"):
                s += "\n"
            widget.insert(tk.END, s)
            widget.see("1.0")
            widget.config(state="disabled")

