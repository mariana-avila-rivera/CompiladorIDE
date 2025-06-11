# -*- coding: utf-8 -*-
"""
Widget de visualización del árbol sintáctico
Contiene la clase TreeVisualizationWidget para mostrar el árbol de forma gráfica
"""

import tkinter as tk
from tkinter import ttk


class TreeVisualizationWidget:
    """Widget para visualizar el árbol sintáctico de forma gráfica y colapsable"""
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.create_widget()
    
    def create_widget(self):
        """Crea el widget de visualización del árbol"""
        # Frame principal
        self.main_frame = tk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview con scrollbars
        self.tree_frame = tk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview con columnas
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("tipo", "linea", "columna"),
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Posicionar elementos
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configurar grid weights
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)        # Configurar columnas del treeview
        self.tree.heading('#0', text='Árbol Sintáctico (Solo Terminales)', anchor='w')
        self.tree.heading('tipo', text='Tipo de token', anchor='w')
        self.tree.heading('linea', text='Línea', anchor='w')
        self.tree.heading('columna', text='Columna', anchor='w')
        self.tree.column('#0', width=300, minwidth=100)
        self.tree.column('tipo', width=120, minwidth=60)
        self.tree.column('linea', width=60, minwidth=40)
        self.tree.column('columna', width=70, minwidth=40)
        
        # Etiqueta para mostrar cuando no hay árbol
        self.no_tree_label = tk.Label(self.main_frame, 
                                     text="No hay árbol sintáctico para mostrar",
                                     fg="gray")
        
    def mostrar_arbol(self, nodo_raiz):
        """Muestra el árbol sintáctico en el widget"""
        if not nodo_raiz:
            self.mostrar_mensaje("No hay árbol sintáctico para mostrar")
            return
        
        # Limpiar árbol anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ocultar etiqueta de "no hay árbol"
        self.no_tree_label.pack_forget()
          # Mostrar el treeview
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Agregar nodos al árbol
        self._agregar_nodo_al_tree(nodo_raiz, '')
        
        # Expandir todos los nodos inicialmente
        self._expandir_todos()
    
    def _agregar_nodo_al_tree(self, nodo, parent_id):
        """Recursivamente agrega nodos al treeview mostrando solo terminales organizados"""
        # Obtener el valor del nodo
        valor_nodo = nodo.valor if hasattr(nodo, 'valor') else nodo.tipo
        
        # Omitir nodos epsilon
        if valor_nodo == 'ε':
            return parent_id
        
        # Verificar si el nodo es terminal (hoja del árbol)
        hijos = getattr(nodo, 'hijos', [])
        es_terminal = len(hijos) == 0
        
        # Si es terminal, agregarlo directamente
        if es_terminal:
            # Extraer info de token si está disponible
            tipo = getattr(nodo, 'token_tipo', None)
            linea = getattr(nodo, 'token_linea', None)
            columna = getattr(nodo, 'token_columna', None)
            
            # Si es NodoArbol, buscar en token_info
            if hasattr(nodo, 'token_info') and nodo.token_info:
                tipo = nodo.token_info.get('tipo')
                linea = nodo.token_info.get('linea')
                columna = nodo.token_info.get('columna')
            
            # Insertar el nodo terminal
            node_id = self.tree.insert(
                parent_id, 'end',
                text=valor_nodo,
                values=(tipo if tipo else '', linea if linea else '', columna if columna else ''),
                open=True
            )
            return node_id
        else:
            # Recopilar todos los terminales de este subárbol
            terminales = self._recopilar_terminales(nodo)
            
            # Si no hay terminales, no hacer nada
            if not terminales:
                return parent_id
            
            # Crear estructura según el tipo de nodo
            if valor_nodo == 'programa':
                # Para programa, no crear nodo, solo procesar hijos
                for hijo in hijos:
                    self._agregar_nodo_al_tree(hijo, parent_id)
                return parent_id
            elif valor_nodo in ['declaracion_variable', 'asignacion', 'seleccion', 'iteracion', 'sent_out', 'expresion_simple', 'termino']:
                # Para estos nodos, crear agrupación con el primer terminal significativo
                terminal_principal = self._encontrar_terminal_principal(terminales, valor_nodo)
                if terminal_principal:
                    node_id = self._crear_nodo_terminal(terminal_principal, parent_id)
                    # Agregar otros terminales como hijos
                    for terminal in terminales:
                        if terminal != terminal_principal:
                            self._crear_nodo_terminal(terminal, node_id)
                    return node_id
                else:
                    # Si no hay terminal principal, agregar todos como hermanos
                    for terminal in terminales:
                        self._crear_nodo_terminal(terminal, parent_id)
                    return parent_id
            else:
                # Para otros nodos, agregar terminales directamente o procesar hijos
                if len(terminales) == 1:
                    return self._crear_nodo_terminal(terminales[0], parent_id)
                else:
                    for hijo in hijos:
                        self._agregar_nodo_al_tree(hijo, parent_id)
                    return parent_id
    
    def _recopilar_terminales(self, nodo):
        """Recopila todos los nodos terminales de un subárbol"""
        terminales = []
        
        def recopilar_recursivo(n):
            if getattr(n, 'valor', getattr(n, 'tipo', '')) == 'ε':
                return
            
            hijos = getattr(n, 'hijos', [])
            if len(hijos) == 0:  # Es terminal
                terminales.append(n)
            else:
                for hijo in hijos:
                    recopilar_recursivo(hijo)
        
        recopilar_recursivo(nodo)
        return terminales
    
    def _encontrar_terminal_principal(self, terminales, tipo_nodo):
        """Encuentra el terminal principal para usar como nodo agrupador"""
        if not terminales:
            return None
        
        # Para asignaciones, buscar el operador
        if tipo_nodo == 'asignacion':
            for terminal in terminales:
                valor = getattr(terminal, 'valor', '')
                if valor in ['=', '+=', '-=', '*=', '/=', '++', '--']:
                    return terminal
        
        # Para declaraciones de variable, buscar el tipo
        elif tipo_nodo == 'declaracion_variable':
            for terminal in terminales:
                valor = getattr(terminal, 'valor', '')
                if valor in ['int', 'float', 'bool']:
                    return terminal
        
        # Para selecciones, buscar if
        elif tipo_nodo == 'seleccion':
            for terminal in terminales:
                valor = getattr(terminal, 'valor', '')
                if valor == 'if':
                    return terminal
        
        # Para expresiones con operadores
        elif tipo_nodo in ['expresion_simple', 'termino']:
            for terminal in terminales:
                valor = getattr(terminal, 'valor', '')
                if valor in ['+', '-', '*', '/', '%', '^', '<', '>', '<=', '>=', '==', '!=']:
                    return terminal
        
        # Si no se encuentra terminal principal específico, usar el primero
        return terminales[0] if terminales else None
    
    def _crear_nodo_terminal(self, terminal, parent_id):
        """Crea un nodo terminal en el árbol"""
        valor = getattr(terminal, 'valor', getattr(terminal, 'tipo', ''))
        
        # Extraer info de token si está disponible
        tipo = getattr(terminal, 'token_tipo', None)
        linea = getattr(terminal, 'token_linea', None)
        columna = getattr(terminal, 'token_columna', None)
        
        # Si es NodoArbol, buscar en token_info
        if hasattr(terminal, 'token_info') and terminal.token_info:
            tipo = terminal.token_info.get('tipo')
            linea = terminal.token_info.get('linea')
            columna = terminal.token_info.get('columna')
        
        # Insertar el nodo terminal
        node_id = self.tree.insert(
            parent_id, 'end',
            text=valor,
            values=(tipo if tipo else '', linea if linea else '', columna if columna else ''),
            open=True
        )
        return node_id
    
    def _expandir_todos(self):
        """Expande todos los nodos del árbol"""
        def expandir_recursivo(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expandir_recursivo(child)
        
        for item in self.tree.get_children():
            expandir_recursivo(item)
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje cuando no hay árbol"""
        # Ocultar treeview
        self.tree_frame.pack_forget()
        
        # Actualizar y mostrar etiqueta
        self.no_tree_label.config(text=mensaje)
        self.no_tree_label.pack(expand=True)
    
    def limpiar(self):
        """Limpia el widget"""
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
        self.mostrar_mensaje("No hay árbol sintáctico para mostrar")
