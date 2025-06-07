import tkinter as tk
from tkinter import ttk

class AnalizadorSintactico:
    def __init__(self):
        self.gramatica = self._definir_gramatica()
        self.terminales = self._obtener_terminales()
        self.no_terminales = self._obtener_no_terminales()
        self.primeros = {}
        self.siguientes = {}
        self.tabla_ll1 = {}
        self.arbol_sintactico = None
        self.errores = []  # Lista para almacenar errores sintácticos
        
    def _definir_gramatica(self):
        """Define las reglas de la gramática"""
        return {
            'programa': [['main', '{', 'lista_declaracion', '}', ';']],
            'lista_declaracion': [
                ['declaracion', 'lista_declaracion'],
                ['ε']
            ],
            'declaracion': [
                ['declaracion_variable'],
                ['sentencia']
            ],
            'declaracion_variable': [['tipo', 'lista_identificadores', ';']],
            'lista_identificadores': [['id', 'lista_identificadores_aux']],
            'lista_identificadores_aux': [
                [',', 'id', 'lista_identificadores_aux'],
                ['ε']
            ],
            'tipo': [['int'], ['float'], ['bool']],
            'sentencia': [
                ['seleccion'], ['iteracion'], ['repeticion'], 
                ['sent_in'], ['sent_out'], ['asignacion']
            ],
            'asignacion': [['id', 'asignacion_op']],
            'asignacion_op': [
                ['=', 'expresion', ';'],
                ['++', ';'],
                ['--', ';']
            ],
            'seleccion': [['if', '(', 'expresion', ')', 'then', 'lista_sentencias', 'seleccion_aux']],
            'seleccion_aux': [
                ['else', 'lista_sentencias', 'end',';'],
                ['end', ';']
            ],
            'iteracion': [['while', '(', 'expresion', ')', 'lista_sentencias', 'end', ';']],
            'repeticion': [
                ['do', 'lista_sentencias', 'until', '(', 'expresion', ')', ';'],
                ['do', 'lista_sentencias', 'while', '(', 'expresion', ')', 'lista_sentencias', 'end', ';']
            ],
            'sent_in': [['cin', '>>', 'id', ';']],
            'sent_out': [['cout', '<<', 'lista_salida', ';']],
            'lista_salida': [['elemento_salida', 'lista_salida_aux']],
            'lista_salida_aux': [
                ['<<', 'elemento_salida', 'lista_salida_aux'],
                ['ε']
            ],
            'elemento_salida': [['cadena'], ['expresion']],
            'lista_sentencias': [
                ['sentencia', 'lista_sentencias'],
                ['ε']
            ],
            'expresion': [['expresion_simple', 'expresion_aux']],
            'expresion_aux': [
                ['rel_op', 'expresion_simple'],
                ['ε']
            ],
            'rel_op': [['<'], ['<='], ['>'], ['>='], ['=='], ['!=']],
            'expresion_simple': [['termino', 'expresion_simple_aux']],
            'expresion_simple_aux': [
                ['suma_op', 'termino', 'expresion_simple_aux'],
                ['ε']
            ],
            'suma_op': [['+'], ['-']],
            'termino': [['componente', 'termino_aux']],
            'termino_aux': [
                ['operador_termino', 'componente', 'termino_aux'],
                ['ε']
            ],
            'operador_termino': [['mult_op'], ['^']],
            'mult_op': [['*'], ['/'], ['%']],
            'componente': [
                ['(', 'expresion', ')'],
                ['numero'],
                ['id'],
                ['booleano'],
                ['!', 'componente']
            ],
            'booleano': [['true'], ['false']],
            'cadena': [['"cualquier_texto"']]
        }
    
    def _obtener_terminales(self):
        """Obtiene todos los símbolos terminales de la gramática"""
        terminales = set()
        for producciones in self.gramatica.values():
            for produccion in producciones:
                for simbolo in produccion:
                    if simbolo not in self.gramatica and simbolo != 'ε':
                        terminales.add(simbolo)
        terminales.add('$')  # Símbolo de fin de cadena
        return terminales
    
    def _obtener_no_terminales(self):
        """Obtiene todos los no terminales de la gramática"""
        return set(self.gramatica.keys())
    
    def calcular_primeros(self):
        """Calcula los conjuntos PRIMEROS para todos los símbolos"""
        # Inicializar conjuntos PRIMEROS
        for simbolo in self.no_terminales | self.terminales:
            self.primeros[simbolo] = set()
        
        # Inicializar PRIMEROS para epsilon
        self.primeros['ε'] = {'ε'}
        
        # PRIMEROS de terminales
        for terminal in self.terminales:
            self.primeros[terminal].add(terminal)
        
        # Repetir hasta que no haya cambios
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                size_anterior = len(self.primeros[no_terminal])
                
                for produccion in self.gramatica[no_terminal]:
                    if produccion == ['ε']:
                        self.primeros[no_terminal].add('ε')
                    else:
                        self._calcular_primeros_produccion(no_terminal, produccion)
                
                if len(self.primeros[no_terminal]) > size_anterior:
                    cambio = True
    
    def _calcular_primeros_produccion(self, no_terminal, produccion):
        """Calcula PRIMEROS para una producción específica"""
        i = 0
        while i < len(produccion):
            simbolo = produccion[i]
            
            # Agregar PRIMEROS(simbolo) - {ε} a PRIMEROS(no_terminal)
            primeros_simbolo = self.primeros[simbolo] - {'ε'}
            self.primeros[no_terminal].update(primeros_simbolo)
            
            # Si ε no está en PRIMEROS(simbolo), parar
            if 'ε' not in self.primeros[simbolo]:
                break
            
            i += 1
        
        # Si todos los símbolos pueden derivar ε, agregar ε
        if i == len(produccion):
            self.primeros[no_terminal].add('ε')
    
    def calcular_siguientes(self):
        """Calcula los conjuntos SIGUIENTES para todos los no terminales"""
        # Inicializar conjuntos SIGUIENTES
        for no_terminal in self.no_terminales:
            self.siguientes[no_terminal] = set()
        
        # SIGUIENTES del símbolo inicial contiene $
        self.siguientes['programa'].add('$')
        
        # Repetir hasta que no haya cambios
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                for produccion in self.gramatica[no_terminal]:
                    if produccion != ['ε']:
                        size_anterior = sum(len(self.siguientes[nt]) for nt in self.no_terminales)
                        self._calcular_siguientes_produccion(no_terminal, produccion)
                        size_actual = sum(len(self.siguientes[nt]) for nt in self.no_terminales)
                        
                        if size_actual > size_anterior:
                            cambio = True
    
    def _calcular_siguientes_produccion(self, no_terminal, produccion):
        """Calcula SIGUIENTES para una producción específica"""
        for i, simbolo in enumerate(produccion):
            if simbolo in self.no_terminales:
                # Obtener PRIMEROS de la subcadena siguiente
                beta = produccion[i+1:]
                primeros_beta = self._calcular_primeros_cadena(beta)
                
                # Agregar PRIMEROS(β) - {ε} a SIGUIENTES(A)
                self.siguientes[simbolo].update(primeros_beta - {'ε'})
                  # Si ε ∈ PRIMEROS(β), agregar SIGUIENTES(no_terminal) a SIGUIENTES(A)
                if 'ε' in primeros_beta or not beta:
                    self.siguientes[simbolo].update(self.siguientes[no_terminal])
    
    def _calcular_primeros_cadena(self, cadena):
        """Calcula PRIMEROS de una cadena de símbolos"""
        if not cadena:
            return {'ε'}
        
        resultado = set()
        
        for simbolo in cadena:
            # Verificar si el símbolo existe en primeros
            if simbolo not in self.primeros:
                if simbolo == 'ε':
                    self.primeros[simbolo] = {'ε'}
                else:
                    # Si es un terminal no reconocido, agregarlo
                    self.primeros[simbolo] = {simbolo}
            
            primeros_simbolo = self.primeros[simbolo] - {'ε'}
            resultado.update(primeros_simbolo)
            
            if 'ε' not in self.primeros[simbolo]:
                break
        else:
            resultado.add('ε')
        
        return resultado
    
    def construir_tabla_ll1(self):
        """Construye la tabla de análisis LL(1)"""
        self.tabla_ll1 = {}
        
        # Inicializar tabla
        for no_terminal in self.no_terminales:
            self.tabla_ll1[no_terminal] = {}
            for terminal in self.terminales:
                self.tabla_ll1[no_terminal][terminal] = None
        
        # Llenar la tabla
        for no_terminal in self.no_terminales:
            for i, produccion in enumerate(self.gramatica[no_terminal]):
                # Para cada terminal en PRIMEROS(producción)
                primeros_prod = self._calcular_primeros_cadena(produccion)
                
                for terminal in primeros_prod - {'ε'}:
                    if self.tabla_ll1[no_terminal][terminal] is None:
                        self.tabla_ll1[no_terminal][terminal] = (no_terminal, produccion)
                    else:
                        # Conflicto en la tabla
                        print(f"Conflicto en M[{no_terminal}, {terminal}]")
                  # Si ε ∈ PRIMEROS(producción)
                if 'ε' in primeros_prod:
                    for terminal in self.siguientes[no_terminal]:
                        if self.tabla_ll1[no_terminal][terminal] is None:
                            self.tabla_ll1[no_terminal][terminal] = (no_terminal, produccion)
                        else:
                            print(f"Conflicto en M[{no_terminal}, {terminal}]")
    
    def analizar(self, tokens):
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
                    if self._intentar_recuperacion(pila, tokens_input, indice):
                        indice += 1  # Saltar el token actual
                        exito_general = False
                        continue
                    else:
                        exito_general = False
                        break
            
            # Si el tope es no terminal
            elif tope in self.no_terminales:
                token_busqueda = self._mapear_token_a_terminal(token_actual, tipo_token)
                
                if token_busqueda in self.tabla_ll1[tope] and self.tabla_ll1[tope][token_busqueda] is not None:
                    produccion = self.tabla_ll1[tope][token_busqueda][1]
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
                    if self._intentar_recuperacion(pila, tokens_input, indice):
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
    
    def _intentar_recuperacion(self, pila, tokens_input, indice):
        """Intenta recuperarse de un error sintáctico siguiendo la estrategia LL(1)"""
        if indice >= len(tokens_input) - 1:  # Si estamos en el último token
            return False
            
        tope = pila[-1]
        token_actual, tipo_token, linea, columna = tokens_input[indice]
        
        # Si el tope es un no terminal, intentamos encontrar un token válido
        if tope in self.no_terminales:
            # Obtener los conjuntos First y Follow del no terminal
            first = self.primeros[tope]
            follow = self.siguientes[tope]
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
    
    def obtener_errores(self):
        """Retorna la lista de errores encontrados"""
        return self.errores
    
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
    
    def inicializar(self):
        """Inicializa el analizador calculando primeros, siguientes y tabla LL(1)"""
        print("Calculando conjuntos PRIMEROS...")
        self.calcular_primeros()
        
        print("Calculando conjuntos SIGUIENTES...")
        self.calcular_siguientes()
        
        print("Construyendo tabla LL(1)...")
        self.construir_tabla_ll1()
        
        print("Analizador sintáctico inicializado correctamente")
    
    def mostrar_conjuntos(self):
        """Muestra los conjuntos PRIMEROS y SIGUIENTES"""
        print("\nConjuntos PRIMEROS:")
        for simbolo in sorted(self.primeros.keys()):
            if simbolo in self.no_terminales:
                print(f"PRIMEROS({simbolo}) = {{{', '.join(sorted(self.primeros[simbolo]))}}}")
        
        print("\nConjuntos SIGUIENTES:")
        for simbolo in sorted(self.siguientes.keys()):
            print(f"SIGUIENTES({simbolo}) = {{{', '.join(sorted(self.siguientes[simbolo]))}}}")


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

def analizar_sintacticamente(tokens):
    """Función principal para análisis sintáctico"""
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    exito, arbol = analizador.analizar(tokens)
    
    if exito:
        print("\n" + "="*50)
        print("ÁRBOL SINTÁCTICO:")
        print("="*50)
        arbol.mostrar_arbol()
        
        # Construir el AST
        ast_builder = ASTBuilder()
        ast = ast_builder.construir_ast(arbol)
        
        print("\n" + "="*50)
        print("ÁRBOL SINTÁCTICO ABSTRACTO (AST):")
        print("="*50)
        ast.mostrar_arbol()
        
        return True, arbol, ast
    else:
        return False, None, None

def leer_tokens_desde_archivo(archivo_path):
    """Lee tokens desde un archivo de texto con formato: tipo lexema linea columna"""
    tokens = []
    try:
        with open(archivo_path, 'r', encoding='utf-8') as file:
            for linea_num, linea in enumerate(file, 1):
                linea = linea.strip()
                if linea and not linea.startswith('#'):  # Ignorar líneas vacías y comentarios
                    partes = linea.split('\t')  # Asumiendo separación por tabulación
                    if len(partes) >= 4:
                        tipo = partes[0]
                        lexema = partes[1]
                        linea_token = int(partes[2])
                        columna_token = int(partes[3])
                        tokens.append((tipo, lexema, linea_token, columna_token))
                    else:
                        # Intento con separación por espacios
                        partes = linea.split()
                        if len(partes) >= 4:
                            tipo = partes[0]
                            lexema = partes[1]
                            linea_token = int(partes[2])
                            columna_token = int(partes[3])
                            tokens.append((tipo, lexema, linea_token, columna_token))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_path}")
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
    
    return tokens


def analizar_sintacticamente_desde_archivo(archivo_tokens):
    """Función principal para análisis sintáctico desde archivo"""
    tokens = leer_tokens_desde_archivo(archivo_tokens)
    
    if not tokens:
        print("No se pudieron leer tokens del archivo")
        return False, None, None, []
    
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    exito, arbol = analizador.analizar(tokens)
    errores = analizador.obtener_errores()
    
    if exito:
        # Construir el AST
        ast_builder = ASTBuilder()
        ast = ast_builder.construir_ast(arbol)
        return exito, arbol, ast, errores
    else:
        return exito, arbol, None, errores
