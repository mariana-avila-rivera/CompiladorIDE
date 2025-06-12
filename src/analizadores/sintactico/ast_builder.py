# -*- coding: utf-8 -*-
"""
Constructor del Árbol Sintáctico Abstracto (AST)
Contiene las clases NodoAST y ASTBuilder para construir un AST a partir del árbol sintáctico
"""


class NodoAST:
    """Nodo para el Árbol Sintáctico Abstracto (AST)"""
    def __init__(self, tipo, valor=None, hijos=None, token_tipo=None, token_linea=None, token_columna=None):
        self.tipo = tipo  # Tipo de nodo
        self.valor = valor  # Valor del nodo
        self.hijos = hijos if hijos is not None else []
        self.atributos = {}  # Diccionario para atributos adicionales
        
        # Atributos de token para compatibilidad con tree_visualization
        self.token_tipo = token_tipo if token_tipo else ""
        self.token_linea = token_linea if token_linea else ""
        self.token_columna = token_columna if token_columna else ""
        
        # Para compatibilidad con la visualización - crear siempre como dict
        self.token_info = {
            'tipo': self.token_tipo,
            'linea': self.token_linea,
            'columna': self.token_columna
        }

    def agregar_hijo(self, hijo):
        """Agrega un hijo al nodo"""
        self.hijos.append(hijo)

    def agregar_atributo(self, nombre, valor):
        """Agrega un atributo al nodo"""
        self.atributos[nombre] = valor

    def mostrar_arbol(self, nivel=0, prefijo=""):
        """Muestra el árbol de forma visual"""
        # Construir la representación del nodo
        nodo_str = f"{self.tipo}"
        if self.valor is not None and self.valor != self.tipo:
            nodo_str += f": {self.valor}"
        
        # Mostrar atributos si existen
        if self.atributos:
            attrs = ", ".join(f"{k}={v}" for k, v in self.atributos.items())
            nodo_str += f" [{attrs}]"
        
        print(f"{prefijo}{'└── ' if nivel > 0 else ''}{nodo_str}")
        
        # Mostrar hijos
        for i, hijo in enumerate(self.hijos):
            es_ultimo = i == len(self.hijos) - 1
            nuevo_prefijo = prefijo + ("    " if nivel > 0 and es_ultimo else "│   " if nivel > 0 else "")
            hijo.mostrar_arbol(nivel + 1, nuevo_prefijo)

    def to_dict(self):
        """Convierte el nodo y sus hijos a un diccionario para facilitar la visualización"""
        return {
            'tipo': self.tipo,
            'valor': self.valor,
            'atributos': self.atributos,
            'hijos': [hijo.to_dict() for hijo in self.hijos]
        }


class ASTBuilder:
    """Constructor del Árbol Sintáctico Abstracto - Filtra y organiza el árbol sintáctico"""
    def __init__(self):
        self.arbol = None

    def construir_ast(self, arbol_sintactico):
        """Convierte el árbol sintáctico en un AST limpio y organizado"""
        if not arbol_sintactico:
            return None
        
        # Procesar el árbol eliminando nodos de gramática innecesarios
        resultado = self._procesar_nodo(arbol_sintactico)
        
        # SOLUCIÓN: Asegurar que SIEMPRE retornemos un nodo único
        if isinstance(resultado, list):
            # Si el procesamiento retorna una lista, crear un nodo raíz
            nodo_raiz = NodoAST(tipo="programa", valor="programa")
            for elemento in resultado:
                if elemento:  # Solo agregar elementos válidos
                    nodo_raiz.agregar_hijo(elemento)
            self.arbol = nodo_raiz
        else:
            self.arbol = resultado
            
        return self.arbol

    def _procesar_nodo(self, nodo_original):
        """Procesa un nodo filtrando y reorganizando según sea necesario"""
        if not nodo_original:
            return None
        
        valor = self._obtener_valor_nodo(nodo_original)
        
        # Omitir nodos epsilon
        if valor == 'ε':
            return None
        
        # Lista de nodos de gramática que debemos omitir (pasar sus hijos directamente)
        nodos_a_omitir = [
            'programa', 'lista_declaracion', 'lista_declaracion_aux',
            'declaracion', 'declaracion_variable', 'lista_identificadores', 
            'lista_identificadores_aux', 'sentencia', 'asignacion',
            'expresion', 'expresion_simple', 'expresion_simple_aux',
            'termino', 'termino_aux', 'componente', 'factor',
            'seleccion', 'iteracion', 'sent_out', 'sent_in',
            'expresion_aux', 'factor_aux', 'sentencia_aux',
            'lista_sentencias', 'lista_salida', 'lista_salida_aux',
            'elemento_salida'
        ]
        
        hijos_originales = getattr(nodo_original, 'hijos', [])
        
        # Si es un nodo a omitir, procesar sus hijos directamente
        if valor in nodos_a_omitir:
            hijos_procesados = []
            for hijo in hijos_originales:
                hijo_procesado = self._procesar_nodo(hijo)
                if hijo_procesado:
                    if isinstance(hijo_procesado, list):
                        hijos_procesados.extend(hijo_procesado)
                    else:
                        hijos_procesados.append(hijo_procesado)
            
            # CAMBIO IMPORTANTE: Siempre retornar una lista para mantener consistencia
            return hijos_procesados
        
        # Para nodos terminales o importantes, crear el nodo AST
        token_info = getattr(nodo_original, 'token_info', None)
        token_tipo = None
        token_linea = None
        token_columna = None
        
        if token_info:
            token_tipo = token_info.get('tipo', '')
            token_linea = token_info.get('linea', '')
            token_columna = token_info.get('columna', '')
        
        # Crear nodo AST
        nodo_ast = NodoAST(
            tipo=valor,
            valor=valor,
            token_tipo=token_tipo,
            token_linea=token_linea,
            token_columna=token_columna
        )
        
        # Procesar hijos
        for hijo in hijos_originales:
            hijo_procesado = self._procesar_nodo(hijo)
            if hijo_procesado:
                if isinstance(hijo_procesado, list):
                    # Si el hijo procesado es una lista, agregar cada elemento
                    for elemento in hijo_procesado:
                        nodo_ast.agregar_hijo(elemento)
                else:
                    nodo_ast.agregar_hijo(hijo_procesado)
        
        return nodo_ast
    
    def _obtener_valor_nodo(self, nodo):
        """Obtiene el valor de un nodo de forma consistente"""
        if hasattr(nodo, 'valor'):
            return nodo.valor
        elif hasattr(nodo, 'tipo'):
            return nodo.tipo
        else:
            return str(nodo)

    def obtener_arbol(self):
        """Retorna el árbol AST construido"""
        return self.arbol

    def limpiar(self):
        """Limpia el árbol AST"""
        self.arbol = None
