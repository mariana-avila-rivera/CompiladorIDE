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
        self.tree.heading('#0', text='Estructura del Programa', anchor='w')
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
        
        # Agregar nodos al árbol con lógica de agrupación
        self._construir_arbol_organizado(nodo_raiz, '')
        
        # Expandir todos los nodos inicialmente
        self._expandir_todos()
    
    def _construir_arbol_organizado(self, nodo_raiz, parent_id):
        """Construye el árbol con la estructura organizada correcta"""
        if not nodo_raiz:
            return parent_id
            
        # Si el nodo raíz es "programa", procesar sus hijos con lógica especial
        if self._obtener_valor_nodo(nodo_raiz) == "programa":
            return self._procesar_programa(nodo_raiz, parent_id)
        else:
            return self._agregar_nodo_con_estructura(nodo_raiz, parent_id)
    
    def _procesar_programa(self, nodo_programa, parent_id):
        """Procesa el nodo programa organizando su contenido"""
        hijos = getattr(nodo_programa, 'hijos', [])
        
        if not hijos:
            return parent_id
        
        # Buscar el patrón main { ... }
        main_index = -1
        llave_index = -1
        
        for i, hijo in enumerate(hijos):
            valor = self._obtener_valor_nodo(hijo)
            if valor == 'main' and main_index == -1:
                main_index = i
            elif valor == '{' and llave_index == -1:
                llave_index = i
        
        if main_index != -1 and llave_index != -1:
            # Crear estructura: main -> { -> contenido
            main_nodo = hijos[main_index]
            main_id = self._crear_nodo_desplegable(main_nodo, parent_id)
            
            # Crear nodo para la llave
            llave_nodo = hijos[llave_index]
            llave_id = self._crear_nodo_desplegable(llave_nodo, main_id)
            
            # Agregar todo el contenido después de { como hijos de la llave
            for i, hijo in enumerate(hijos):
                if i != main_index and i != llave_index:
                    valor = self._obtener_valor_nodo(hijo)
                    if valor != '}':  # Omitir llave de cierre
                        self._agregar_nodo_con_estructura(hijo, llave_id)
            
            return main_id
        else:
            # Si no hay patrón main {}, agregar hijos directamente
            for hijo in hijos:
                self._agregar_nodo_con_estructura(hijo, parent_id)
            return parent_id
    
    def _agregar_nodo_con_estructura(self, nodo, parent_id):
        """Agrega un nodo aplicando lógica de estructura según su tipo"""
        valor = self._obtener_valor_nodo(nodo)
        hijos = getattr(nodo, 'hijos', [])
        
        # Si es un operador, crear estructura de operador
        if self._es_operador(valor):
            return self._crear_estructura_operador(nodo, parent_id)
        
        # Si es un tipo de dato con identificadores, crear estructura de declaración
        elif self._es_tipo_dato(valor) and len(hijos) > 0:
            return self._crear_estructura_declaracion(nodo, parent_id)
        
        # Si es una palabra clave de control, crear estructura de control
        elif self._es_palabra_control(valor):
            return self._crear_estructura_control(nodo, parent_id)
        
        # Si es cout/cin, crear estructura de entrada/salida
        elif valor in ['cout', 'cin']:
            return self._crear_estructura_io(nodo, parent_id)
        
        # Si tiene hijos, crear nodo desplegable
        elif len(hijos) > 0:
            node_id = self._crear_nodo_desplegable(nodo, parent_id)
            for hijo in hijos:
                self._agregar_nodo_con_estructura(hijo, node_id)
            return node_id
        
        # Si es terminal, crear nodo simple
        else:
            return self._crear_nodo_simple(nodo, parent_id)
    
    def _es_operador(self, valor):
        """Verifica si es un operador"""
        operadores = ['=', '+=', '-=', '*=', '/=', '+', '-', '*', '/', '%', '^', 
                     '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!']
        return valor in operadores
    
    def _es_tipo_dato(self, valor):
        """Verifica si es un tipo de dato"""
        tipos = ['int', 'float', 'bool', 'string', 'char', 'double']
        return valor in tipos
    
    def _es_palabra_control(self, valor):
        """Verifica si es una palabra clave de control"""
        palabras = ['if', 'then', 'else', 'while', 'for', 'switch', 'case', 'default']
        return valor in palabras
    
    def _crear_estructura_operador(self, nodo, parent_id):
        """Crea estructura para operadores: operador -> operandos"""
        operador_id = self._crear_nodo_desplegable(nodo, parent_id)
        
        # Agregar operandos como hijos del operador
        hijos = getattr(nodo, 'hijos', [])
        for hijo in hijos:
            self._agregar_nodo_con_estructura(hijo, operador_id)
        
        return operador_id
    
    def _crear_estructura_declaracion(self, nodo, parent_id):
        """Crea estructura para declaraciones: tipo -> identificadores"""
        tipo_id = self._crear_nodo_desplegable(nodo, parent_id)
        
        # Agregar identificadores como hijos del tipo
        hijos = getattr(nodo, 'hijos', [])
        for hijo in hijos:
            valor_hijo = self._obtener_valor_nodo(hijo)
            if valor_hijo not in [',', ';']:  # Omitir comas y punto y coma
                self._agregar_nodo_con_estructura(hijo, tipo_id)
        
        return tipo_id
    
    def _crear_estructura_control(self, nodo, parent_id):
        """Crea estructura para estructuras de control"""
        control_id = self._crear_nodo_desplegable(nodo, parent_id)
        
        # Agregar contenido como hijos
        hijos = getattr(nodo, 'hijos', [])
        for hijo in hijos:
            self._agregar_nodo_con_estructura(hijo, control_id)
        
        return control_id
    
    def _crear_estructura_io(self, nodo, parent_id):
        """Crea estructura para entrada/salida: cout/cin -> contenido"""
        io_id = self._crear_nodo_desplegable(nodo, parent_id)
        
        # Agregar contenido como hijos
        hijos = getattr(nodo, 'hijos', [])
        for hijo in hijos:
            valor_hijo = self._obtener_valor_nodo(hijo)
            if valor_hijo not in ['<<', '>>', ';']:  # Omitir operadores de flujo
                self._agregar_nodo_con_estructura(hijo, io_id)
        
        return io_id
    
    def _crear_nodo_desplegable(self, nodo, parent_id):
        """Crea un nodo desplegable"""
        valor = self._obtener_valor_nodo(nodo)
        
        # Obtener información del token de forma segura
        tipo = ""
        linea = ""
        columna = ""
        
        # Intentar obtener token_info de diferentes formas
        token_info = getattr(nodo, 'token_info', None)
        
        if token_info and isinstance(token_info, dict):
            tipo = token_info.get('tipo', '')
            linea = token_info.get('linea', '')
            columna = token_info.get('columna', '')
        else:
            # Intentar obtener directamente de los atributos del nodo
            tipo = getattr(nodo, 'token_tipo', '')
            linea = getattr(nodo, 'token_linea', '')
            columna = getattr(nodo, 'token_columna', '')
        
        # Insertar nodo desplegable
        node_id = self.tree.insert(
            parent_id, 'end',
            text=valor,
            values=(tipo, linea, columna),
            open=True
        )
        
        return node_id
    
    def _crear_nodo_simple(self, nodo, parent_id):
        """Crea un nodo terminal simple"""
        return self._crear_nodo_desplegable(nodo, parent_id)
    
    def _obtener_valor_nodo(self, nodo):
        """Obtiene el valor de un nodo de forma consistente"""
        if hasattr(nodo, 'valor'):
            return nodo.valor
        elif hasattr(nodo, 'tipo'):
            return nodo.tipo
        else:
            return str(nodo)
    
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
        self.tree_frame.pack_forget()
        self.no_tree_label.config(text=mensaje)
        self.no_tree_label.pack(expand=True)
    
    def limpiar(self):
        """Limpia el widget"""
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
        self.mostrar_mensaje("No hay árbol sintáctico para mostrar")
