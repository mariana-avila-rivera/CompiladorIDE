# -*- coding: utf-8 -*-
"""
Árbol sintáctico
Contiene la clase NodoArbol para construir el árbol sintáctico
"""


class NodoArbol:
    """Nodo para construir el árbol sintáctico"""
    def __init__(self, valor, token_info=None):
        self.valor = valor
        self.hijos = []
        self.padre = None
        self.token_info = token_info  # Diccionario con tipo, linea, columna si es un token
    
    def agregar_hijo(self, hijo):
        hijo.padre = self
        self.hijos.append(hijo)
    
    def mostrar_arbol(self, nivel=0, prefijo=""):
        """Muestra el árbol de forma visual"""
        print(f"{prefijo}{'└── ' if nivel > 0 else ''}{self.valor}")
        
        for i, hijo in enumerate(self.hijos):
            es_ultimo = i == len(self.hijos) - 1
            nuevo_prefijo = prefijo + ("    " if nivel > 0 and es_ultimo else "│   " if nivel > 0 else "")
            hijo.mostrar_arbol(nivel + 1, nuevo_prefijo)
    
    def to_dict(self):
        """Convierte el nodo y sus hijos a un diccionario para facilitar la visualización"""
        return {
            'valor': self.valor,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }
