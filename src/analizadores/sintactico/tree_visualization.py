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
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar columnas del treeview
        self.tree.heading('#0', text='Árbol Sintáctico Abstracto (AST)', anchor='w')
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
        """Recursivamente agrega nodos al treeview"""
        # Extraer info de token si está disponible
        tipo = getattr(nodo, 'token_tipo', None)
        linea = getattr(nodo, 'token_linea', None)
        columna = getattr(nodo, 'token_columna', None)
        # Si es NodoArbol, buscar en token_info
        if hasattr(nodo, 'token_info') and nodo.token_info:
            tipo = nodo.token_info.get('tipo')
            linea = nodo.token_info.get('linea')
            columna = nodo.token_info.get('columna')
        # Insertar el nodo actual
        node_id = self.tree.insert(
            parent_id, 'end',
            text=nodo.valor if hasattr(nodo, 'valor') else nodo.tipo,
            values=(tipo if tipo else '', linea if linea else '', columna if columna else ''),
            open=True
        )
        # Agregar hijos
        for hijo in getattr(nodo, 'hijos', []):
            self._agregar_nodo_al_tree(hijo, node_id)
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
