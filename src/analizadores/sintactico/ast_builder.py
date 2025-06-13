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
        # Definir precedencia de operadores
        self.precedencia = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '%': 2,
            '^': 3
        }

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
        hijos_originales = getattr(nodo_original, 'hijos', [])

        simbolos_omitir = {'(', ')', ',', ';', '{', '}', '[', ']', '<<', '>>'}

        # Si es el nodo raíz 'programa', hacer que 'main' sea la raíz del AST
        if valor == 'programa' and len(hijos_originales) >= 1:
            main_nodo = None
            hijos_main = []
            for hijo in hijos_originales:
                hijo_valor = self._obtener_valor_nodo(hijo)
                if hijo_valor == 'main':
                    main_nodo = self._procesar_nodo(hijo)
                elif hijo_valor not in simbolos_omitir:
                    procesado = self._procesar_nodo(hijo)
                    if procesado:
                        if isinstance(procesado, list):
                            hijos_main.extend(procesado)
                        else:
                            hijos_main.append(procesado)
            if main_nodo is None:
                main_nodo = NodoAST(tipo='main', valor='main')
            for hijo in hijos_main:
                main_nodo.agregar_hijo(hijo)
            return main_nodo

        # Omitir nodos epsilon, None y símbolos de puntuación
        if valor == 'ε' or valor is None or valor in simbolos_omitir:
            return None

        nodos_a_omitir = [
            'lista_declaracion', 'lista_declaracion_aux',
            'declaracion', 'lista_identificadores', 'lista_identificadores_aux',
            'sentencia', 'asignacion', 'expresion', 'expresion_simple', 'expresion_simple_aux',
            'termino', 'termino_aux', 'componente', 'factor',
            'expresion_aux', 'factor_aux', 'sentencia_aux',
            'lista_sentencias', 'lista_salida', 'lista_salida_aux', 'elemento_salida'
        ]

        reglas_token = [
            'asignacion_op', 'suma_op', 'operador_termino', 'mult_op', 'tipo', 'rel_op'
        ]

        # Si es una declaración de variable, hacer el tipo raíz y los identificadores hijos
        if valor == 'declaracion_variable' and len(hijos_originales) >= 2:
            tipo_nodo = self._procesar_nodo(hijos_originales[0])
            identificadores = self._procesar_nodo(hijos_originales[1])
            if tipo_nodo is None:
                return identificadores
            if isinstance(identificadores, list):
                for ident in identificadores:
                    tipo_nodo.agregar_hijo(ident)
            elif identificadores:
                tipo_nodo.agregar_hijo(identificadores)
            return tipo_nodo

        # Si es un bloque de control (if, while, etc.), la palabra reservada es la raíz
        if valor == 'seleccion' and len(hijos_originales) >= 1:
            palabra_if = self._procesar_nodo(hijos_originales[0])  # 'if'
            condicion = self._procesar_nodo(hijos_originales[2])   # expresion
            palabra_then = self._procesar_nodo(hijos_originales[4])  # 'then'
            sentencias_then = self._procesar_nodo(hijos_originales[5])
            seleccion_aux = self._procesar_nodo(hijos_originales[6])
            if isinstance(palabra_if, NodoAST):
                if condicion:
                    palabra_if.agregar_hijo(condicion)
                # 'then' como raíz
                if palabra_then is None:
                    palabra_then = NodoAST(tipo='then', valor='then')
                # Agregar sentencias como hijos de 'then'
                if sentencias_then:
                    if isinstance(sentencias_then, list):
                        for s in sentencias_then:
                            palabra_then.agregar_hijo(s)
                    else:
                        palabra_then.agregar_hijo(sentencias_then)
                palabra_if.agregar_hijo(palabra_then)
                # 'else' y 'end' ya se agregan como raíces en seleccion_aux
                if seleccion_aux:
                    if isinstance(seleccion_aux, list):
                        for s in seleccion_aux:
                            palabra_if.agregar_hijo(s)
                    else:
                        palabra_if.agregar_hijo(seleccion_aux)
                return palabra_if

        if valor == 'seleccion_aux' and hijos_originales:
            palabra_else = self._procesar_nodo(hijos_originales[0])
            if len(hijos_originales) == 4:
                sentencias_else = self._procesar_nodo(hijos_originales[1])
                palabra_end = self._procesar_nodo(hijos_originales[2])
                if isinstance(palabra_else, NodoAST):
                    if sentencias_else:
                        if isinstance(sentencias_else, list):
                            for s in sentencias_else:
                                palabra_else.agregar_hijo(s)
                        else:
                            palabra_else.agregar_hijo(sentencias_else)
                    if palabra_end:
                        palabra_else.agregar_hijo(palabra_end)
                    return palabra_else
            else:
                palabra_end = palabra_else
                return palabra_end

        if valor == 'iteracion' and len(hijos_originales) >= 1:
            palabra_while = self._procesar_nodo(hijos_originales[0])  # 'while'
            condicion = self._procesar_nodo(hijos_originales[2])
            sentencias = self._procesar_nodo(hijos_originales[4])
            palabra_end = self._procesar_nodo(hijos_originales[5])
            if isinstance(palabra_while, NodoAST):
                if condicion:
                    palabra_while.agregar_hijo(condicion)
                if sentencias:
                    if isinstance(sentencias, list):
                        for s in sentencias:
                            palabra_while.agregar_hijo(s)
                    else:
                        palabra_while.agregar_hijo(sentencias)
                if palabra_end:
                    palabra_while.agregar_hijo(palabra_end)
                return palabra_while

        # Si es un bloque de repetición do-until o do-while
        if valor == 'repeticion' and len(hijos_originales) >= 1:
            palabra_do = self._procesar_nodo(hijos_originales[0])  # 'do'
            sentencias = self._procesar_nodo(hijos_originales[1])
            palabra_cond = self._procesar_nodo(hijos_originales[2])  # 'until' o 'while'
            condicion = None
            if len(hijos_originales) > 4:
                condicion = self._procesar_nodo(hijos_originales[4])
            elif len(hijos_originales) > 3:
                condicion = self._procesar_nodo(hijos_originales[3])
            if isinstance(palabra_do, NodoAST):
                if sentencias:
                    if isinstance(sentencias, list):
                        for s in sentencias:
                            palabra_do.agregar_hijo(s)
                    else:
                        palabra_do.agregar_hijo(sentencias)
                if palabra_cond:
                    if condicion:
                        palabra_cond.agregar_hijo(condicion)
                    palabra_do.agregar_hijo(palabra_cond)
                return palabra_do

        # Si es una sentencia de salida (cout) o entrada (cin)
        if valor == 'sent_out' and len(hijos_originales) >= 1:
            cout_nodo = self._procesar_nodo(hijos_originales[0])  # 'cout'
            if cout_nodo is None:
                cout_nodo = NodoAST(tipo='cout', valor='cout')
            # Agregar todos los hijos relevantes (operador y valor) en orden
            for hijo in hijos_originales[1:]:
                hijo_proc = self._procesar_nodo(hijo)
                if hijo_proc is not None:
                    if isinstance(hijo_proc, list):
                        for elem in hijo_proc:
                            if elem is not None:
                                cout_nodo.agregar_hijo(elem)
                    else:
                        cout_nodo.agregar_hijo(hijo_proc)
            return cout_nodo

        if valor == 'sent_in' and len(hijos_originales) >= 1:
            cin_nodo = self._procesar_nodo(hijos_originales[0])  # 'cin'
            if cin_nodo is None:
                cin_nodo = NodoAST(tipo='cin', valor='cin')
            for hijo in hijos_originales[1:]:
                hijo_proc = self._procesar_nodo(hijo)
                if hijo_proc is not None:
                    if isinstance(hijo_proc, list):
                        for elem in hijo_proc:
                            if elem is not None:
                                cin_nodo.agregar_hijo(elem)
                    else:
                        cin_nodo.agregar_hijo(hijo_proc)
            return cin_nodo

        if valor in nodos_a_omitir:
            hijos_procesados = []
            for hijo in hijos_originales:
                hijo_procesado = self._procesar_nodo(hijo)
                if hijo_procesado:
                    if isinstance(hijo_procesado, list):
                        hijos_procesados.extend(hijo_procesado)
                    else:
                        hijos_procesados.append(hijo_procesado)
            if valor in ['expresion', 'expresion_simple', 'termino']:
                return self._reorganizar_expresion(hijos_procesados)
            return hijos_procesados

        if valor in reglas_token and hijos_originales:
            primer_hijo = hijos_originales[0]
            hijo_procesado = self._procesar_nodo(primer_hijo)
            if isinstance(hijo_procesado, NodoAST):
                valor_real = hijo_procesado.valor
                token_info = hijo_procesado.token_info
            else:
                valor_real = str(hijo_procesado)
                token_info = None
            if valor_real is None or valor_real in simbolos_omitir:
                return None
            nodo_ast = NodoAST(
                tipo=valor_real,
                valor=valor_real,
                token_tipo=token_info.get('tipo', '') if token_info else '',
                token_linea=token_info.get('linea', '') if token_info else '',
                token_columna=token_info.get('columna', '') if token_info else ''
            )
            for hijo in hijos_originales[1:]:
                hijo_procesado = self._procesar_nodo(hijo)
                if hijo_procesado:
                    if isinstance(hijo_procesado, list):
                        for elem in hijo_procesado:
                            nodo_ast.agregar_hijo(elem)
                    else:
                        nodo_ast.agregar_hijo(hijo_procesado)
            return nodo_ast

        token_info = getattr(nodo_original, 'token_info', None)
        token_tipo = None
        token_linea = None
        token_columna = None
        if token_info:
            token_tipo = token_info.get('tipo', '')
            token_linea = token_info.get('linea', '')
            token_columna = token_info.get('columna', '')
        if valor is None or valor in simbolos_omitir:
            return None
        nodo_ast = NodoAST(
            tipo=valor,
            valor=valor,
            token_tipo=token_tipo,
            token_linea=token_linea,
            token_columna=token_columna
        )
        for hijo in hijos_originales:
            hijo_procesado = self._procesar_nodo(hijo)
            if hijo_procesado:
                if isinstance(hijo_procesado, list):
                    for elemento in hijo_procesado:
                        nodo_ast.agregar_hijo(elemento)
                else:
                    nodo_ast.agregar_hijo(hijo_procesado)
        return nodo_ast

    def _reorganizar_expresion(self, nodos):
        """Reorganiza una expresión según la precedencia de operadores, incluyendo relacionales y lógicos"""
        if not nodos:
            return None
        # Filtrar nodos None antes de procesar
        nodos = [n for n in nodos if n is not None]
        if not nodos:
            return None
        if len(nodos) == 1:
            return nodos[0]
        # Precedencia extendida: menor número = menor precedencia (más arriba en el árbol)
        precedencia_ext = {
            '||': 0, '&&': 1, 'or': 0, 'and': 1, # lógicos
            '==': 2, '!=': 2, '<': 2, '<=': 2, '>': 2, '>=': 2, # relacionales
            '+': 3, '-': 3,
            '*': 4, '/': 4, '%': 4,
            '^': 5
        }
        min_precedencia = float('inf')
        min_index = -1
        for i, nodo in enumerate(nodos):
            if isinstance(nodo, NodoAST) and nodo.valor in precedencia_ext:
                prec = precedencia_ext[nodo.valor]
                if prec < min_precedencia:
                    min_precedencia = prec
                    min_index = i
        if min_index == -1:
            return nodos
        operador = nodos[min_index]
        izquierda = self._reorganizar_expresion(nodos[:min_index])
        derecha = self._reorganizar_expresion(nodos[min_index+1:])
        # Solo agregar hijos si no son None
        if izquierda is not None:
            if isinstance(izquierda, list):
                for nodo in izquierda:
                    if nodo is not None:
                        operador.agregar_hijo(nodo)
            else:
                operador.agregar_hijo(izquierda)
        if derecha is not None:
            if isinstance(derecha, list):
                for nodo in derecha:
                    if nodo is not None:
                        operador.agregar_hijo(nodo)
            else:
                operador.agregar_hijo(derecha)
        return operador

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
