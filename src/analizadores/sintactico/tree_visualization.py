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
        self.tree.heading('#0', text='Estructura del Programa (Terminales Organizados)', anchor='w')
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
        self.no_tree_label.pack_forget()        # Mostrar el treeview
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
            return self._crear_nodo_terminal(nodo, parent_id)
        else:
            # Aplicar la nueva lógica simplificada
            return self._procesar_nodo_no_terminal(nodo, parent_id)
    
    def _procesar_nodo_no_terminal(self, nodo, parent_id):
        """Procesa un nodo no terminal creando jerarquías apropiadas"""
        valor_nodo = nodo.valor if hasattr(nodo, 'valor') else nodo.tipo
        hijos = getattr(nodo, 'hijos', [])
        
        # Definir categorías de nodos que deben ser raíces
        operadores_aritmeticos = ['+', '-', '*', '/', '%', '^']
        operadores_relacionales = ['<', '>', '<=', '>=', '==', '!=']
        operadores_asignacion = ['=', '+=', '-=', '*=', '/=']
        operadores_logicos = ['&&', '||', '!']
        tipos_datos = ['int', 'float', 'bool', 'string', 'char', 'double']
        palabras_clave = ['main', 'if', 'else', 'while', 'for', 'do', 'switch', 'case', 'default']
        entrada_salida = ['cout', 'cin', '<<', '>>']
        
        # Recopilar todos los terminales de este subárbol
        terminales = self._recopilar_terminales(nodo)
        
        # Buscar el terminal más importante para ser raíz
        nodo_raiz = self._encontrar_nodo_raiz(terminales, {
            'main': palabras_clave,
            'tipos': tipos_datos,
            'asignacion': operadores_asignacion,
            'aritmeticos': operadores_aritmeticos,
            'relacionales': operadores_relacionales,
            'logicos': operadores_logicos,
            'io': entrada_salida
        })
        
        if nodo_raiz:
            # Crear el nodo raíz
            root_id = self._crear_nodo_terminal(nodo_raiz, parent_id)
            
            # Organizar los demás terminales bajo la raíz según contexto
            self._organizar_terminales_bajo_raiz(nodo_raiz, terminales, root_id, hijos)
            
            return root_id
        else:
            # Si no hay un nodo clave claro, usar estrategia de fallback
            return self._procesar_como_grupo(hijos, parent_id)
    
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
    
    def _encontrar_nodo_raiz(self, terminales, categorias):
        """Encuentra el terminal más importante para ser raíz según prioridades"""
        # Orden de prioridad (de mayor a menor importancia)
        prioridades = ['main', 'tipos', 'asignacion', 'aritmeticos', 'relacionales', 'logicos', 'io']
        
        for prioridad in prioridades:
            if prioridad in categorias:
                for terminal in terminales:
                    valor = getattr(terminal, 'valor', '')
                    if valor in categorias[prioridad]:
                        return terminal
        return None
    
    def _organizar_terminales_bajo_raiz(self, nodo_raiz, terminales, root_id, hijos_originales):
        """Organiza los terminales restantes bajo el nodo raíz de manera inteligente"""
        valor_raiz = getattr(nodo_raiz, 'valor', '')
        
        # Filtrar terminales (excluir el que ya es raíz y épsilon)
        otros_terminales = []
        for terminal in terminales:
            valor_terminal = getattr(terminal, 'valor', '')
            if valor_terminal != valor_raiz and valor_terminal != 'ε':
                otros_terminales.append(terminal)
        
        # Lógica específica por tipo de raíz
        if valor_raiz == 'main':
            self._organizar_main(otros_terminales, root_id, hijos_originales)
        elif valor_raiz in ['int', 'float', 'bool', 'string', 'char', 'double']:
            self._organizar_declaracion_tipo(otros_terminales, root_id)
        elif valor_raiz in ['=', '+=', '-=', '*=', '/=']:
            self._organizar_asignacion(otros_terminales, root_id)
        elif valor_raiz in ['+', '-', '*', '/', '%', '^']:
            self._organizar_operacion_aritmetica(otros_terminales, root_id)
        elif valor_raiz in ['<', '>', '<=', '>=', '==', '!=']:
            self._organizar_operacion_relacional(otros_terminales, root_id)
        elif valor_raiz == 'if':
            self._organizar_estructura_if(otros_terminales, root_id, hijos_originales)
        elif valor_raiz in ['cout', 'cin']:
            self._organizar_entrada_salida(otros_terminales, root_id)
        else:
            # Fallback: agregar todos los terminales como hijos
            for terminal in otros_terminales:
                self._crear_nodo_terminal(terminal, root_id)
    
    def _organizar_main(self, terminales, parent_id, hijos_originales):
        """Organiza el contenido del main procesando grupos de hijos"""
        # Para main, procesamos los hijos originales de manera recursiva
        # en lugar de solo los terminales
        for hijo in hijos_originales:
            valor_hijo = getattr(hijo, 'valor', getattr(hijo, 'tipo', ''))
            if valor_hijo != 'main' and valor_hijo != 'ε':
                self._agregar_nodo_al_tree(hijo, parent_id)
    
    def _organizar_declaracion_tipo(self, terminales, parent_id):
        """Organiza una declaración de tipo (ej: int x, y;)"""
        # Los identificadores van como hijos del tipo
        for terminal in terminales:
            valor = getattr(terminal, 'valor', '')
            # Solo agregar identificadores y números, no símbolos como , ;
            if valor.isalnum() or valor.replace('_', '').isalnum():
                self._crear_nodo_terminal(terminal, parent_id)
    
    def _organizar_asignacion(self, terminales, parent_id):
        """Organiza una asignación (ej: x = 5;)"""
        # Primer terminal es la variable, resto son la expresión
        if len(terminales) >= 1:
            # Variable (lado izquierdo)
            self._crear_nodo_terminal(terminales[0], parent_id)
        if len(terminales) >= 2:
            # Expresión (lado derecho) - puede ser múltiple para expresiones complejas
            if len(terminales) == 2:
                # Simple: x = 5
                self._crear_nodo_terminal(terminales[1], parent_id)
            else:
                # Compleja: x = y + 5, crear subgrupo para la expresión
                expr_id = self.tree.insert(parent_id, 'end', text="expresión", 
                                         values=('Expresión', '', ''))
                for terminal in terminales[1:]:
                    self._crear_nodo_terminal(terminal, expr_id)
    
    def _organizar_operacion_aritmetica(self, terminales, parent_id):
        """Organiza una operación aritmética (ej: x + y)"""
        # Los operandos van como hijos del operador
        for terminal in terminales:
            self._crear_nodo_terminal(terminal, parent_id)
    
    def _organizar_operacion_relacional(self, terminales, parent_id):
        """Organiza una operación relacional (ej: x < y)"""
        # Los operandos van como hijos del operador relacional
        for terminal in terminales:
            self._crear_nodo_terminal(terminal, parent_id)
    
    def _organizar_estructura_if(self, terminales, parent_id, hijos_originales):
        """Organiza una estructura if con sus componentes"""
        # Para if, necesitamos procesar la condición y las sentencias
        # Buscar nodos específicos en los hijos originales
        for hijo in hijos_originales:
            valor_hijo = getattr(hijo, 'valor', getattr(hijo, 'tipo', ''))
            if valor_hijo != 'if' and valor_hijo != 'ε':
                self._agregar_nodo_al_tree(hijo, parent_id)
    
    def _organizar_entrada_salida(self, terminales, parent_id):
        """Organiza sentencias de entrada/salida (ej: cout << x;)"""
        # Los elementos van como hijos del cout/cin
        for terminal in terminales:
            valor = getattr(terminal, 'valor', '')
            if valor not in ['<<', '>>', ';']:  # Excluir operadores de flujo y ;
                self._crear_nodo_terminal(terminal, parent_id)
    
    def _procesar_como_grupo(self, hijos, parent_id):
        """Procesa un grupo de hijos cuando no hay un nodo raíz claro"""
        for hijo in hijos:
            self._agregar_nodo_al_tree(hijo, parent_id)
        return parent_id
