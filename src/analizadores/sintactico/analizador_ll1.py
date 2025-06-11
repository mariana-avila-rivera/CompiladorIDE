# -*- coding: utf-8 -*-
"""
Analizador LL(1)
Contiene la lógica principal del análisis sintáctico LL(1) con manejo de errores
"""

from .arbol_sintactico import NodoArbol


class AnalizadorLL1:
    def __init__(self, terminales, no_terminales):
        self.terminales = terminales
        self.no_terminales = no_terminales
        self.errores = []
        
    def analizar(self, tokens, tabla_ll1, primeros, siguientes):
        """Analiza una lista de tokens usando la tabla LL(1) con manejo de errores mejorado"""
        self.errores = []  # Reiniciar errores
        
        # Preparar tokens
        tokens_input = []
        for token in tokens:
            if len(token) >= 4 and token[1].strip():  # Validar formato del token
                tokens_input.append((token[1], token[0], token[2], token[3]))  # lexema, tipo, linea, columna
        tokens_input.append(('$', 'EOF', 0, 0))
        
        # Inicializar pila y índice
        pila = ['$', 'programa']
        indice = 0
        arbol = NodoArbol('programa')
        pila_nodos = [None, arbol]
        
        print("Análisis sintáctico:")
        print(f"{'Pila':<30} {'Entrada':<20} {'Acción'}")
        print("-" * 70)
        
        exito_general = True
        
        while len(pila) > 1 and indice < len(tokens_input):
            tope = pila[-1]
            nodo_actual = pila_nodos[-1]
            
            if indice < len(tokens_input):
                token_actual, tipo_token, linea, columna = tokens_input[indice]
            else:
                self._agregar_error("Error fatal: Se acabaron los tokens inesperadamente", 0, 0)
                exito_general = False
                break
            
            print(f"{str(pila):<30} {token_actual:<20}", end=" ")
            
            # Si el tope es terminal
            if tope in self.terminales:
                if tope == token_actual or self._tokens_coinciden(tope, token_actual, tipo_token):
                    pila.pop()
                    # Asociar info de token al nodo hoja
                    token_info = {'tipo': tipo_token, 'linea': linea, 'columna': columna}
                    nodo_actual.token_info = token_info
                    pila_nodos.pop()
                    indice += 1
                    print(f"Coincide {tope}")
                else:
                    error_msg = f"Se esperaba '{tope}', se encontró '{token_actual}'"
                    self._agregar_error(error_msg, linea, columna)
                    print(f"Error: {error_msg}")
                    
                    # Intento de recuperación de error
                    if self._intentar_recuperacion(pila, tokens_input, indice, primeros, siguientes):
                        indice += 1  # Saltar el token actual
                        exito_general = False
                        continue
                    else:
                        exito_general = False
                        break
            
            # Si el tope es no terminal
            elif tope in self.no_terminales:
                token_busqueda = self._mapear_token_a_terminal(token_actual, tipo_token)
                
                if token_busqueda in tabla_ll1[tope] and tabla_ll1[tope][token_busqueda] is not None:
                    produccion = tabla_ll1[tope][token_busqueda][1]
                    pila.pop()
                    pila_nodos.pop()
                    
                    print(f"Aplicar {tope} → {' '.join(produccion)}")
                    
                    # Agregar hijos al nodo del árbol
                    if produccion != ['ε']:
                        for simbolo in produccion:
                            hijo = NodoArbol(simbolo)
                            nodo_actual.agregar_hijo(hijo)
                        
                        # Agregar símbolos a la pila en orden inverso
                        for simbolo in reversed(produccion):
                            pila.append(simbolo)
                        
                        # Agregar nodos a la pila en orden inverso
                        for hijo in reversed(nodo_actual.hijos):
                            pila_nodos.append(hijo)
                    else:
                        # Producción epsilon
                        hijo_epsilon = NodoArbol('ε')
                        nodo_actual.agregar_hijo(hijo_epsilon)
                else:
                    error_msg = f"No existe regla para el no-terminal '{tope}' con el token '{token_actual}'"
                    self._agregar_error(error_msg, linea, columna)
                    print(f"Error: {error_msg}")
                    
                    # Intento de recuperación de error
                    if self._intentar_recuperacion(pila, tokens_input, indice, primeros, siguientes):
                        indice += 1  # Saltar el token actual
                        exito_general = False
                        continue
                    else:
                        exito_general = False
                        break
            else:
                error_msg = f"Símbolo desconocido en la pila: '{tope}'"
                self._agregar_error(error_msg, linea, columna)
                print(f"Error: {error_msg}")
                exito_general = False
                break
        
        # Verificar si se completó correctamente
        if len(pila) == 1 and indice == len(tokens_input) - 1 and tokens_input[indice][0] == '$':
            if exito_general and not self.errores:
                print("Análisis completado exitosamente")
                return True, arbol
            else:
                print("Análisis completado con errores")
                return False, arbol
        else:
            if indice < len(tokens_input) - 1:
                self._agregar_error("Tokens restantes en la entrada", 0, 0)
            if len(pila) > 1:
                self._agregar_error("Símbolos restantes en la pila", 0, 0)
            print("Error: Análisis incompleto")
            return False, arbol
    
    def _agregar_error(self, mensaje, linea, columna):
        """Agrega un error a la lista de errores"""
        error = {
            'tipo': 'Error Sintáctico',
            'mensaje': mensaje,
            'linea': linea,
            'columna': columna
        }
        self.errores.append(error)
    
    def _intentar_recuperacion(self, pila, tokens_input, indice, primeros, siguientes):
        """Intenta recuperarse de un error sintáctico siguiendo la estrategia LL(1)"""
        if indice >= len(tokens_input) - 1:  # Si estamos en el último token
            return False
            
        tope = pila[-1]
        token_actual, tipo_token, linea, columna = tokens_input[indice]
        
        # Si el tope es un no terminal, intentamos encontrar un token válido
        if tope in self.no_terminales:
            # Obtener los conjuntos First y Follow del no terminal
            first = primeros.get(tope, set())
            follow = siguientes.get(tope, set())
            conjunto_sincronizacion = first | follow
            
            # Saltar tokens hasta encontrar uno en el conjunto de sincronización
            while indice < len(tokens_input) - 1:
                indice += 1
                token_siguiente, tipo_siguiente, _, _ = tokens_input[indice]
                token_mapeado = self._mapear_token_a_terminal(token_siguiente, tipo_siguiente)
                
                if token_mapeado in conjunto_sincronizacion:
                    # Encontramos un token válido, podemos continuar
                    return True
                    
            # Si llegamos aquí, no encontramos un token válido
            return False
            
        # Si el tope es un terminal, simplemente saltamos el token actual
        return True
    
    def _tokens_coinciden(self, simbolo_gramatica, token, tipo_token):
        """Verifica si un token coincide con un símbolo de la gramática"""
        mapeo = {
            'id': 'Identificador',
            'numero': ['Número entero', 'Número real'],
            'true': 'true',
            'false': 'false',
            'cadena': 'String'
        }
        
        if simbolo_gramatica in mapeo:
            tipos_esperados = mapeo[simbolo_gramatica]
            if isinstance(tipos_esperados, list):
                return tipo_token in tipos_esperados
            else:
                return tipo_token == tipos_esperados or token == simbolo_gramatica
        
        return simbolo_gramatica == token
    
    def _mapear_token_a_terminal(self, token, tipo_token):
        """Mapea un token a su símbolo terminal correspondiente usando la información del archivo JSON"""
        # Mapeo directo para palabras reservadas
        palabras_reservadas = {
            'main', 'if', 'then', 'else', 'end', 'while', 'do', 'until',
            'cin', 'cout', 'int', 'float', 'bool', 'true', 'false'
        }
        
        if token in palabras_reservadas:
            return token
        
        # Mapeo por tipo de token según el JSON
        mapeo_tipos = {
            'Identificador': 'id',
            'Número entero': 'numero',
            'Número real': 'numero',
            'String': 'cadena',
            'Palabra reservada': lambda t: t.lower() if t.lower() in palabras_reservadas else 'id',
            'Operador aritmético': lambda t: t if t in {'+', '-', '*', '/', '%', '^', '++', '--'} else None,
            'Operador relacional': lambda t: t if t in {'<', '<=', '>', '>=', '==', '!='} else None,
            'Operador lógico': lambda t: t.lower() if t.lower() in {'and', 'or', 'not'} else None,
            'Operador de asignación': lambda t: t if t in {'=', '+=', '-=', '*=', '/=', '%=', '^='} else None,
            'Operador de shift': lambda t: t if t in {'<<', '>>'} else None,
            'Símbolo': lambda t: t if t in {'(', ')', '{', '}', '[', ']', ';', ','} else None
        }
        
        if tipo_token in mapeo_tipos:
            mapeo = mapeo_tipos[tipo_token]
            if callable(mapeo):
                resultado = mapeo(token)
                if resultado is not None:
                    return resultado
            else:
                return mapeo
        
        # Si no se encuentra un mapeo específico, intentar usar el token directamente
        return token
