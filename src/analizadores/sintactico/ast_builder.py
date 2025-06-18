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
            '||': 0, 'or': 0,
            '&&': 1, 'and': 1,
            '==': 2, '!=': 2, '<': 2, '<=': 2, '>': 2, '>=': 2,
            '+': 3, '-': 3,
            '*': 4, '/': 4, '%': 4,
            '^': 5
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
                if elemento:
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

        # NUEVA LÓGICA: Transformar ++ y -- en asignaciones
        if valor == 'asignacion' and len(hijos_originales) >= 2:
            id_nodo = self._procesar_nodo(hijos_originales[0])  # identificador
            asignacion_op = hijos_originales[1]  # nodo asignacion_op
            
            # Verificar si es ++ o --
            asignacion_hijos = getattr(asignacion_op, 'hijos', [])
            if asignacion_hijos:
                operador_valor = self._obtener_valor_nodo(asignacion_hijos[0])
                
                if operador_valor == '++':
                    # Transformar id++ en id = id + 1
                    return self._crear_asignacion_incremento(id_nodo, '+')
                elif operador_valor == '--':
                    # Transformar id-- en id = id - 1  
                    return self._crear_asignacion_incremento(id_nodo, '-')
                # Si no es ++ o --, procesar como asignación normal
                else:
                    # Crear nodo de asignación normal
                    nodo_asignacion = self._procesar_nodo(asignacion_hijos[0])  # el operador =
                    if nodo_asignacion is None:
                        nodo_asignacion = NodoAST(tipo='=', valor='=')
                    
                    # Agregar variable como primer hijo
                    nodo_asignacion.agregar_hijo(id_nodo)
                    
                    # Procesar y agregar la expresión como segundo hijo
                    if len(asignacion_hijos) > 1:
                        expresion = self._procesar_nodo(asignacion_hijos[1])
                        if expresion:
                            nodo_asignacion.agregar_hijo(expresion)
                    
                    return nodo_asignacion
    
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
            return main_nodo        # Omitir nodos epsilon, None y símbolos de puntuación
        if valor == 'ε' or valor is None or valor in simbolos_omitir:
            return None        # MANEJO ESPECÍFICO PARA COMPONENTE: extraer solo la expresión interna de los paréntesis
        if valor == 'componente' and len(hijos_originales) == 3:
            # componente -> '(' expresion ')'
            if (self._obtener_valor_nodo(hijos_originales[0]) == '(' and 
                self._obtener_valor_nodo(hijos_originales[2]) == ')'):
                # Retornar solo la expresión interna procesada
                return self._procesar_nodo(hijos_originales[1])
        
        # Si es componente con un solo hijo (numero, id, etc.), procesarlo normalmente
        if valor == 'componente' and len(hijos_originales) == 1:
            return self._procesar_nodo(hijos_originales[0])        # MANEJO ESPECÍFICO PARA TERMINO: omitir solo si tiene un hijo, procesar como expresión si tiene múltiples
        if valor == 'termino':
            hijos_procesados = []
            for hijo in hijos_originales:
                hijo_procesado = self._procesar_nodo(hijo)
                if hijo_procesado:
                    if isinstance(hijo_procesado, list):
                        hijos_procesados.extend(hijo_procesado)
                    else:
                        hijos_procesados.append(hijo_procesado)
            
            print(f"DEBUG: termino procesado con {len(hijos_procesados)} hijos:")
            for i, hijo in enumerate(hijos_procesados):
                if hasattr(hijo, 'valor'):
                    print(f"  [{i}] {hijo.valor} con {len(hijo.hijos) if hasattr(hijo, 'hijos') else 0} hijos")
                    if hasattr(hijo, 'hijos') and len(hijo.hijos) > 0:
                        print(f"      hijos: {[h.valor if hasattr(h, 'valor') else str(h) for h in hijo.hijos]}")
                else:
                    print(f"  [{i}] {str(hijo)}")
            
            # Si solo tiene un hijo, omitir el nodo termino
            if len(hijos_procesados) == 1:
                print(f"DEBUG: termino retornando hijo único: {hijos_procesados[0].valor if hasattr(hijos_procesados[0], 'valor') else str(hijos_procesados[0])}")
                return hijos_procesados[0]
            # Si tiene múltiples hijos, reorganizar como expresión
            elif len(hijos_procesados) > 1:
                print(f"DEBUG: termino llamando a _reorganizar_expresion con {len(hijos_procesados)} hijos")
                resultado = self._reorganizar_expresion(hijos_procesados)
                print(f"DEBUG: termino retornando resultado: {resultado.valor if hasattr(resultado, 'valor') else str(resultado)}")
                if hasattr(resultado, 'hijos'):
                    print(f"DEBUG: resultado tiene {len(resultado.hijos)} hijos: {[h.valor if hasattr(h, 'valor') else str(h) for h in resultado.hijos]}")
                return resultado
            else:
                return None

        # CORRECCIÓN: Quitar 'asignacion' de nodos_a_omitir ya que se maneja específicamente arriba
        nodos_a_omitir = [
            'lista_declaracion', 'lista_declaracion_aux',
            'declaracion', 'lista_identificadores', 'lista_identificadores_aux',
            'sentencia', 'expresion', 'expresion_simple', 'expresion_simple_aux',
            'termino_aux', 'factor',  # termino se maneja específicamente arriba
            'expresion_aux', 'factor_aux', 'sentencia_aux',
            'lista_sentencias', 'lista_salida', 'lista_salida_aux', 'elemento_salida',
            # Agregar los nuevos no terminales de expresiones lógicas
            'expresion_logica', 'expresion_logica_aux',
            'expresion_and', 'expresion_and_aux',
            'expresion_relacional', 'expresion_relacional_aux'
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
                    if ident:
                        tipo_nodo.agregar_hijo(ident)
            elif identificadores:
                tipo_nodo.agregar_hijo(identificadores)
            return tipo_nodo

        # Si es un bloque de control (if, while, etc.), la palabra reservada es la raíz
        if valor == 'seleccion' and len(hijos_originales) >= 6:
            palabra_if = self._procesar_nodo(hijos_originales[0])  # 'if'
            condicion = self._procesar_nodo(hijos_originales[2])   # expresion
            palabra_then = self._procesar_nodo(hijos_originales[4])  # 'then'
            sentencias_then = self._procesar_nodo(hijos_originales[5])
            seleccion_aux = self._procesar_nodo(hijos_originales[6]) if len(hijos_originales) > 6 else None
            
            if palabra_if is None:
                palabra_if = NodoAST(tipo='if', valor='if')
            
            if condicion:
                palabra_if.agregar_hijo(condicion)
            
            # 'then' como raíz de las sentencias
            if palabra_then is None:
                palabra_then = NodoAST(tipo='then', valor='then')
            
            # Agregar sentencias como hijos de 'then'
            if sentencias_then:
                if isinstance(sentencias_then, list):
                    for sent in sentencias_then:
                        if sent:
                            palabra_then.agregar_hijo(sent)
                else:
                    palabra_then.agregar_hijo(sentencias_then)
            
            palabra_if.agregar_hijo(palabra_then)
            
            # 'else' y 'end' ya se agregan como raíces en seleccion_aux
            if seleccion_aux:
                palabra_if.agregar_hijo(seleccion_aux)
            
            return palabra_if

        if valor == 'seleccion_aux' and hijos_originales:
            palabra_else = self._procesar_nodo(hijos_originales[0])
            if len(hijos_originales) >= 4:
                sentencias_else = self._procesar_nodo(hijos_originales[1])
                palabra_end = self._procesar_nodo(hijos_originales[2])
                if palabra_else is None:
                    palabra_else = NodoAST(tipo='else', valor='else')
                if sentencias_else:
                    if isinstance(sentencias_else, list):
                        for sent in sentencias_else:
                            if sent:
                                palabra_else.agregar_hijo(sent)
                    else:
                        palabra_else.agregar_hijo(sentencias_else)
                return palabra_else
            else:
                palabra_end = palabra_else
                return palabra_end

        if valor == 'iteracion' and len(hijos_originales) >= 6:
            palabra_while = self._procesar_nodo(hijos_originales[0])  # 'while'
            condicion = self._procesar_nodo(hijos_originales[2])
            sentencias = self._procesar_nodo(hijos_originales[4])
            palabra_end = self._procesar_nodo(hijos_originales[5])
            if palabra_while is None:
                palabra_while = NodoAST(tipo='while', valor='while')
            if condicion:
                palabra_while.agregar_hijo(condicion)
            if sentencias:
                if isinstance(sentencias, list):
                    for sent in sentencias:
                        if sent:
                            palabra_while.agregar_hijo(sent)
                else:
                    palabra_while.agregar_hijo(sentencias)
            if palabra_end:
                palabra_while.agregar_hijo(palabra_end)
            return palabra_while

        # Si es un bloque de repetición do-until o do-while
        if valor == 'repeticion' and len(hijos_originales) >= 6:
            palabra_do = self._procesar_nodo(hijos_originales[0])  # 'do'
            sentencias = self._procesar_nodo(hijos_originales[1])
            palabra_cond = self._procesar_nodo(hijos_originales[2])  # 'until' o 'while'
            condicion = None
            if len(hijos_originales) > 4:
                condicion = self._procesar_nodo(hijos_originales[4])
            elif len(hijos_originales) > 3:
                condicion = self._procesar_nodo(hijos_originales[3])
            if palabra_do is None:
                palabra_do = NodoAST(tipo='do', valor='do')
            if sentencias:
                if isinstance(sentencias, list):
                    for sent in sentencias:
                        if sent:
                            palabra_do.agregar_hijo(sent)
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
            
            # Procesar todos los hijos y filtrar símbolos no deseados
            for hijo in hijos_originales[1:]:
                hijo_valor = self._obtener_valor_nodo(hijo)
                # Omitir operadores << explícitamente
                if hijo_valor not in simbolos_omitir:
                    hijo_procesado = self._procesar_nodo(hijo)
                    if hijo_procesado:
                        if isinstance(hijo_procesado, list):
                            for h in hijo_procesado:
                                if h and self._obtener_valor_nodo(h) not in simbolos_omitir:
                                    cout_nodo.agregar_hijo(h)
                        else:
                            cout_nodo.agregar_hijo(hijo_procesado)
            return cout_nodo

        if valor == 'sent_in' and len(hijos_originales) >= 1:
            cin_nodo = self._procesar_nodo(hijos_originales[0])  # 'cin'
            if cin_nodo is None:
                cin_nodo = NodoAST(tipo='cin', valor='cin')
            
            # Procesar todos los hijos y filtrar símbolos no deseados
            for hijo in hijos_originales[1:]:
                hijo_valor = self._obtener_valor_nodo(hijo)
                # Omitir operadores >> explícitamente
                if hijo_valor not in simbolos_omitir:
                    hijo_procesado = self._procesar_nodo(hijo)
                    if hijo_procesado:
                        if isinstance(hijo_procesado, list):
                            for h in hijo_procesado:
                                if h and self._obtener_valor_nodo(h) not in simbolos_omitir:
                                    cin_nodo.agregar_hijo(h)
                        else:
                            cin_nodo.agregar_hijo(hijo_procesado)
            return cin_nodo

        if valor in nodos_a_omitir:
            hijos_procesados = []
            for hijo in hijos_originales:
                hijo_procesado = self._procesar_nodo(hijo)
                if hijo_procesado:
                    if isinstance(hijo_procesado, list):
                        hijos_procesados.extend(hijo_procesado)
                    else:
                        hijos_procesados.append(hijo_procesado)            # Para expresiones, reorganizar según precedencia
            if valor in ['expresion', 'expresion_simple', 'termino', 'expresion_logica', 'expresion_and', 'expresion_relacional']:
                return self._reorganizar_expresion(hijos_procesados)
            
            return hijos_procesados

        if valor in reglas_token and hijos_originales:
            primer_hijo = hijos_originales[0]
            hijo_procesado = self._procesar_nodo(primer_hijo)
            if isinstance(hijo_procesado, NodoAST):
                valor_real = hijo_procesado.valor
                token_info = hijo_procesado.token_info
            else:
                valor_real = self._obtener_valor_nodo(primer_hijo)
                token_info = getattr(primer_hijo, 'token_info', None)
            
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
                    nodo_ast.agregar_hijo(hijo_procesado)
            
            return nodo_ast

        # Para nodos terminales, crear nodo AST
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
                    for h in hijo_procesado:
                        if h and self._obtener_valor_nodo(h) not in simbolos_omitir:
                            nodo_ast.agregar_hijo(h)
                else:
                    if self._obtener_valor_nodo(hijo_procesado) not in simbolos_omitir:
                        nodo_ast.agregar_hijo(hijo_procesado)
        
        return nodo_ast

    def _crear_asignacion_incremento(self, id_nodo, operador):
        """Crea un nodo de asignación para incremento/decremento: variable = variable +/- 1"""
        if not id_nodo:
            return None
        
        # Crear nodo de asignación
        nodo_asignacion = NodoAST(tipo='=', valor='=')
        
        # Lado izquierdo: la variable
        nodo_asignacion.agregar_hijo(id_nodo)
        
        # Lado derecho: variable + 1 o variable - 1
        nodo_operacion = NodoAST(tipo=operador, valor=operador)
        
        # Crear una copia del identificador para el lado derecho
        id_copia = NodoAST(
            tipo=id_nodo.tipo,
            valor=id_nodo.valor,
            token_tipo=id_nodo.token_tipo,
            token_linea=id_nodo.token_linea,
            token_columna=id_nodo.token_columna
        )
        
        # Crear nodo para el número 1
        nodo_uno = NodoAST(tipo='numero', valor='1')
          # Estructura: operador -> [variable, 1]
        nodo_operacion.agregar_hijo(id_copia)
        nodo_operacion.agregar_hijo(nodo_uno)
        
        # Estructura final: = -> [variable, (+ variable 1)]
        nodo_asignacion.agregar_hijo(nodo_operacion)
        
        return nodo_asignacion

    def _reorganizar_expresion(self, nodos):
        """Reorganiza una expresión según la precedencia de operadores con asociatividad izquierda"""
        if not nodos:
            return None
        
        # Filtrar nodos None
        nodos = [n for n in nodos if n is not None]
        if not nodos:
            return None
        if len(nodos) == 1:
            return nodos[0]
        
        print(f"DEBUG: _reorganizar_expresion con {len(nodos)} nodos:")
        for i, nodo in enumerate(nodos):
            if hasattr(nodo, 'valor'):
                print(f"  [{i}] {nodo.valor} con {len(nodo.hijos) if hasattr(nodo, 'hijos') else 0} hijos")
                if hasattr(nodo, 'hijos') and len(nodo.hijos) > 0:
                    print(f"      hijos: {[h.valor if hasattr(h, 'valor') else str(h) for h in nodo.hijos]}")
        
        # Precedencia: menor número = menor precedencia (se evalúa después)
        precedencia = {
            '||': 0, 'or': 0,
            '&&': 1, 'and': 1,
            '==': 2, '!=': 2, '<': 2, '<=': 2, '>': 2, '>=': 2,
            '+': 3, '-': 3,
            '*': 4, '/': 4, '%': 4,
            '^': 5
        }
        
        # CORRECCIÓN: Solo considerar nodos que NO tengan hijos como operadores válidos
        # Los nodos con hijos ya son expresiones procesadas y no deben ser reorganizados
        operador_idx = -1
        min_precedencia = float('inf')
        
        # Buscar de DERECHA a IZQUIERDA para asociatividad izquierda
        for i in range(len(nodos) - 1, -1, -1):
            nodo = nodos[i]
            # CLAVE: Solo considerar como operador si no tiene hijos (es un operador sin procesar)
            if (isinstance(nodo, NodoAST) and 
                nodo.valor in precedencia and 
                len(nodo.hijos) == 0):
                prec = precedencia[nodo.valor]
                print(f"DEBUG: nodo {nodo.valor} en posición {i} tiene precedencia {prec}")
                # Solo actualizar si encontramos menor precedencia
                if prec < min_precedencia:
                    min_precedencia = prec
                    operador_idx = i
                    print(f"DEBUG: nuevo operador seleccionado: {nodo.valor} con precedencia {prec}")
        
        if operador_idx == -1:
            # No hay operadores válidos, retornar el primer nodo si solo hay uno válido
            if len(nodos) == 1:
                return nodos[0]
            # Si hay múltiples nodos pero no operadores, puede ser un error
            print(f"DEBUG: No se encontraron operadores válidos en nodos: {[n.valor if hasattr(n, 'valor') else str(n) for n in nodos]}")
            return nodos[0] if nodos else None
        
        # Construir el árbol con el operador como raíz
        operador = nodos[operador_idx]
        print(f"DEBUG: operador final seleccionado: {operador.valor} en posición {operador_idx}")
        
        # Recursivamente procesar las partes izquierda y derecha
        izquierda = nodos[:operador_idx] if operador_idx > 0 else []
        derecha = nodos[operador_idx + 1:] if operador_idx < len(nodos) - 1 else []
        
        print(f"DEBUG: izquierda ({len(izquierda)} nodos): {[n.valor if hasattr(n, 'valor') else str(n) for n in izquierda]}")
        print(f"DEBUG: derecha ({len(derecha)} nodos): {[n.valor if hasattr(n, 'valor') else str(n) for n in derecha]}")
        
        # Limpiar los hijos existentes del operador
        print(f"DEBUG: operador {operador.valor} antes: {len(operador.hijos)} hijos")
        operador.hijos = []
        
        # Procesar lado izquierdo
        if izquierda:
            nodo_izq = self._reorganizar_expresion(izquierda)
            if nodo_izq is not None:
                if isinstance(nodo_izq, list):
                    operador.hijos.extend([n for n in nodo_izq if n is not None])
                else:
                    operador.hijos.append(nodo_izq)
                    print(f"DEBUG: agregado hijo izquierdo: {nodo_izq.valor if hasattr(nodo_izq, 'valor') else str(nodo_izq)}")
        
        # Procesar lado derecho
        if derecha:
            nodo_der = self._reorganizar_expresion(derecha)
            if nodo_der is not None:
                if isinstance(nodo_der, list):
                    operador.hijos.extend([n for n in nodo_der if n is not None])
                else:
                    operador.hijos.append(nodo_der)
                    print(f"DEBUG: agregado hijo derecho: {nodo_der.valor if hasattr(nodo_der, 'valor') else str(nodo_der)}")
        
        print(f"DEBUG: operador {operador.valor} final: {len(operador.hijos)} hijos: {[h.valor if hasattr(h, 'valor') else str(h) for h in operador.hijos]}")
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
