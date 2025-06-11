# -*- coding: utf-8 -*-
"""
Constructor del Árbol Sintáctico Abstracto (AST)
Contiene las clases NodoAST y ASTBuilder para construir un AST a partir del árbol sintáctico
"""


class NodoAST:
    """Nodo para el Árbol Sintáctico Abstracto (AST)"""
    def __init__(self, tipo, valor=None, hijos=None, token_tipo=None, token_linea=None, token_columna=None):
        self.tipo = tipo  # Tipo de nodo (ej: 'Programa', 'Declaracion', 'Expresion', etc.)
        self.valor = valor  # Valor del nodo (ej: nombre de variable, operador, etc.)
        self.hijos = hijos if hijos is not None else []
        self.atributos = {}  # Diccionario para atributos adicionales (tipo, línea, columna, etc.)
        # Nuevos atributos estándar para token
        self.token_tipo = token_tipo
        self.token_linea = token_linea
        self.token_columna = token_columna

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)

    def agregar_atributo(self, nombre, valor):
        self.atributos[nombre] = valor

    def mostrar_arbol(self, nivel=0, prefijo=""):
        """Muestra el árbol de forma visual"""
        # Construir la representación del nodo
        nodo_str = f"{self.tipo}"
        if self.valor is not None:
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
    """Constructor del Árbol Sintáctico Abstracto"""
    def __init__(self):
        self.arbol = None

    def construir_ast(self, arbol_sintactico):
        """Convierte el árbol sintáctico en un AST"""
        if not arbol_sintactico:
            return None
        
        # Crear nodo raíz del programa
        self.arbol = NodoAST('Programa')
        
        # Procesar el árbol sintáctico
        self._procesar_nodo(arbol_sintactico, self.arbol)
        
        return self.arbol

    def _procesar_nodo(self, nodo_sintactico, nodo_ast):
        """Procesa un nodo del árbol sintáctico y lo convierte en nodo AST"""
        if not nodo_sintactico:
            return

        # Mapeo de tipos de nodos sintácticos a tipos AST
        mapeo_tipos = {
            'programa': self._procesar_programa,
            'lista_declaracion': self._procesar_lista_declaraciones,
            'declaracion': self._procesar_declaracion,
            'declaracion_variable': self._procesar_declaracion_variable,
            'sentencia': self._procesar_sentencia,
            'seleccion': self._procesar_seleccion,
            'iteracion': self._procesar_iteracion,
            'repeticion': self._procesar_repeticion,
            'sent_in': self._procesar_entrada,
            'sent_out': self._procesar_salida,
            'asignacion': self._procesar_asignacion,
            'expresion': self._procesar_expresion,
            'expresion_simple': self._procesar_expresion_simple,
            'termino': self._procesar_termino,
            'componente': self._procesar_componente
        }

        # Obtener el procesador correspondiente al tipo de nodo
        procesador = mapeo_tipos.get(nodo_sintactico.valor.lower())
        if procesador:
            procesador(nodo_sintactico, nodo_ast)
        else:
            # Si no hay procesador específico, procesar los hijos
            for hijo in nodo_sintactico.hijos:
                self._procesar_nodo(hijo, nodo_ast)

    def _procesar_programa(self, nodo, padre_ast):
        """Procesa el nodo programa"""
        for hijo in nodo.hijos:
            if hijo.valor == 'lista_declaracion':
                self._procesar_nodo(hijo, padre_ast)

    def _procesar_lista_declaraciones(self, nodo, padre_ast):
        """Procesa la lista de declaraciones"""
        for hijo in nodo.hijos:
            if hijo.valor != 'ε':
                self._procesar_nodo(hijo, padre_ast)

    def _procesar_declaracion(self, nodo, padre_ast):
        """Procesa una declaración"""
        for hijo in nodo.hijos:
            self._procesar_nodo(hijo, padre_ast)

    def _procesar_declaracion_variable(self, nodo, padre_ast):
        """Procesa una declaración de variable"""
        tipo = None
        variables = []
        
        for hijo in nodo.hijos:
            if hijo.valor in ['int', 'float', 'bool']:
                tipo = hijo.valor
            elif hijo.valor == 'lista_identificadores':
                for var in hijo.hijos:
                    if var.valor == 'id':
                        variables.append(var.hijos[0].valor)
        
        for var in variables:
            nodo_var = NodoAST(tipo)  # Usar el tipo como nombre del nodo
            nodo_var.agregar_atributo('nombre', var)
            padre_ast.agregar_hijo(nodo_var)

    def _procesar_sentencia(self, nodo, padre_ast):
        """Procesa una sentencia"""
        for hijo in nodo.hijos:
            self._procesar_nodo(hijo, padre_ast)

    def _procesar_seleccion(self, nodo, padre_ast):
        """Procesa una sentencia if-then-else"""
        nodo_if = NodoAST('if')  # Usar 'if' como nombre del nodo
        
        # Procesar condición
        for hijo in nodo.hijos:
            if hijo.valor == 'expresion':
                condicion = NodoAST('condicion')
                self._procesar_nodo(hijo, condicion)
                nodo_if.agregar_hijo(condicion)
            elif hijo.valor == 'lista_sentencias':
                cuerpo = NodoAST('then')
                self._procesar_nodo(hijo, cuerpo)
                nodo_if.agregar_hijo(cuerpo)
            elif hijo.valor == 'seleccion_aux':
                for subhijo in hijo.hijos:
                    if subhijo.valor == 'else':
                        else_cuerpo = NodoAST('else')
                        self._procesar_nodo(subhijo.hijos[0], else_cuerpo)
                        nodo_if.agregar_hijo(else_cuerpo)
        
        padre_ast.agregar_hijo(nodo_if)

    def _procesar_iteracion(self, nodo, padre_ast):
        """Procesa una sentencia while"""
        nodo_while = NodoAST('while')  # Usar 'while' como nombre del nodo
        
        for hijo in nodo.hijos:
            if hijo.valor == 'expresion':
                condicion = NodoAST('condicion')
                self._procesar_nodo(hijo, condicion)
                nodo_while.agregar_hijo(condicion)
            elif hijo.valor == 'lista_sentencias':
                cuerpo = NodoAST('cuerpo')
                self._procesar_nodo(hijo, cuerpo)
                nodo_while.agregar_hijo(cuerpo)
        
        padre_ast.agregar_hijo(nodo_while)

    def _procesar_repeticion(self, nodo, padre_ast):
        """Procesa una sentencia do-while o do-until"""
        # Determinar el tipo de repetición
        tipo_rep = 'until' if 'until' in [h.valor for h in nodo.hijos] else 'while'
        nodo_rep = NodoAST('do-' + tipo_rep)  # Usar 'do-while' o 'do-until' como nombre
        
        for hijo in nodo.hijos:
            if hijo.valor == 'expresion':
                condicion = NodoAST('condicion')
                self._procesar_nodo(hijo, condicion)
                nodo_rep.agregar_hijo(condicion)
            elif hijo.valor == 'lista_sentencias':
                cuerpo = NodoAST('cuerpo')
                self._procesar_nodo(hijo, cuerpo)
                nodo_rep.agregar_hijo(cuerpo)
        
        padre_ast.agregar_hijo(nodo_rep)

    def _procesar_entrada(self, nodo, padre_ast):
        """Procesa una sentencia de entrada (cin)"""
        nodo_entrada = NodoAST('cin')  # Usar 'cin' como nombre del nodo
        
        for hijo in nodo.hijos:
            if hijo.valor == 'id':
                nodo_entrada.agregar_atributo('variable', hijo.hijos[0].valor)
        
        padre_ast.agregar_hijo(nodo_entrada)

    def _procesar_salida(self, nodo, padre_ast):
        """Procesa una sentencia de salida (cout)"""
        nodo_salida = NodoAST('cout')  # Usar 'cout' como nombre del nodo
        
        for hijo in nodo.hijos:
            if hijo.valor == 'lista_salida':
                for elemento in hijo.hijos:
                    if elemento.valor == 'elemento_salida':
                        self._procesar_nodo(elemento, nodo_salida)
        
        padre_ast.agregar_hijo(nodo_salida)

    def _procesar_asignacion(self, nodo, padre_ast):
        """Procesa una asignación"""
        operador = '='  # Operador por defecto
        variable = None
        
        for hijo in nodo.hijos:
            if hijo.valor == 'id':
                variable = hijo.hijos[0].valor
            elif hijo.valor == 'asignacion_op':
                for op in hijo.hijos:
                    if op.valor in ['=', '+=', '-=', '*=', '/=', '%=', '^=']:
                        operador = op.valor
                    elif op.valor in ['++', '--']:
                        operador = op.valor
                    elif op.valor == 'expresion':
                        nodo_asig = NodoAST(operador)
                        nodo_asig.agregar_atributo('variable', variable)
                        self._procesar_nodo(op, nodo_asig)
                        padre_ast.agregar_hijo(nodo_asig)

    def _procesar_expresion(self, nodo, padre_ast):
        """Procesa una expresión"""
        if len(nodo.hijos) == 1:
            self._procesar_nodo(nodo.hijos[0], padre_ast)
        else:
            operador = nodo.hijos[1].valor
            nodo_exp = NodoAST(operador)
            self._procesar_nodo(nodo.hijos[0], nodo_exp)
            self._procesar_nodo(nodo.hijos[2], nodo_exp)
            padre_ast.agregar_hijo(nodo_exp)

    def _procesar_expresion_simple(self, nodo, padre_ast):
        """Procesa una expresión simple"""
        if len(nodo.hijos) == 1:
            self._procesar_nodo(nodo.hijos[0], padre_ast)
        else:
            operador = nodo.hijos[1].valor
            nodo_exp = NodoAST(operador)
            self._procesar_nodo(nodo.hijos[0], nodo_exp)
            self._procesar_nodo(nodo.hijos[2], nodo_exp)
            padre_ast.agregar_hijo(nodo_exp)

    def _procesar_termino(self, nodo, padre_ast):
        """Procesa un término"""
        if len(nodo.hijos) == 1:
            self._procesar_nodo(nodo.hijos[0], padre_ast)
        else:
            operador = nodo.hijos[1].valor
            nodo_term = NodoAST(operador)
            self._procesar_nodo(nodo.hijos[0], nodo_term)
            self._procesar_nodo(nodo.hijos[2], nodo_term)
            padre_ast.agregar_hijo(nodo_term)

    def _procesar_componente(self, nodo, padre_ast):
        """Procesa un componente"""
        if len(nodo.hijos) == 1:
            hijo = nodo.hijos[0]
            if hijo.valor == 'id':
                # Buscar información de token si está disponible
                token_info = getattr(hijo, 'token_info', None)
                if token_info:
                    nodo_comp = NodoAST(hijo.hijos[0].valor, token_tipo=token_info.get('tipo'), token_linea=token_info.get('linea'), token_columna=token_info.get('columna'))
                else:
                    nodo_comp = NodoAST(hijo.hijos[0].valor)
                padre_ast.agregar_hijo(nodo_comp)
            elif hijo.valor == 'numero':
                token_info = getattr(hijo, 'token_info', None)
                if token_info:
                    nodo_comp = NodoAST(hijo.hijos[0].valor, token_tipo=token_info.get('tipo'), token_linea=token_info.get('linea'), token_columna=token_info.get('columna'))
                else:
                    nodo_comp = NodoAST(hijo.hijos[0].valor)
                padre_ast.agregar_hijo(nodo_comp)
            elif hijo.valor == 'booleano':
                token_info = getattr(hijo, 'token_info', None)
                if token_info:
                    nodo_comp = NodoAST(hijo.hijos[0].valor, token_tipo=token_info.get('tipo'), token_linea=token_info.get('linea'), token_columna=token_info.get('columna'))
                else:
                    nodo_comp = NodoAST(hijo.hijos[0].valor)
                padre_ast.agregar_hijo(nodo_comp)
        else:
            self._procesar_nodo(nodo.hijos[1], padre_ast)
