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
                ['else', 'lista_sentencias', 'end'],
                ['end']
            ],
            'iteracion': [['while', '(', 'expresion', ')', 'lista_sentencias', 'end']],
            'repeticion': [
                ['do', 'lista_sentencias', 'until', '(', 'expresion', ')', ';'],
                ['do', 'lista_sentencias', 'while', '(', 'expresion', ')', 'lista_sentencias', 'end']
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
                    pila_nodos.pop()
                    indice += 1
                    print(f"Coincide {tope}")
                else:
                    error_msg = f"Se esperaba '{tope}', se encontró '{token_actual}'"
                    self._agregar_error(error_msg, linea, columna)
                    print(f"Error: {error_msg}")
                    
                    # Intento de recuperación de error
                    if self._intentar_recuperacion(pila, tokens_input, indice):
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
        """Intenta recuperarse de un error sintáctico"""
        # Estrategia simple: saltar el token actual
        if indice < len(tokens_input) - 1:
            return True
        return False
    
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
        """Mapea un token a su símbolo terminal correspondiente"""
        # Mapeo directo para palabras reservadas
        palabras_reservadas = {
            'main', 'if', 'then', 'else', 'end', 'while', 'do', 'until',
            'cin', 'cout', 'int', 'float', 'bool', 'true', 'false'
        }
        
        if token in palabras_reservadas:
            return token
        
        # Mapeo por tipo de token
        mapeo_tipos = {
            'Identificador': 'id',
            'Número entero': 'numero',
            'Número real': 'numero',
            'String': 'cadena'
        }
        
        if tipo_token in mapeo_tipos:
            return mapeo_tipos[tipo_token]
        
        # Para operadores y símbolos, usar el token directamente
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
    def __init__(self, valor):
        self.valor = valor
        self.hijos = []
        self.padre = None
    
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
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, 
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
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
        self.tree.heading('#0', text='Árbol Sintáctico', anchor='w')
        self.tree.column('#0', width=300, minwidth=100)
        
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
        # Insertar el nodo actual
        node_id = self.tree.insert(parent_id, 'end', text=nodo.valor, open=True)
        
        # Agregar hijos
        for hijo in nodo.hijos:
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


def analizar_sintacticamente(tokens):
    """Función principal para análisis sintáctico"""
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    # Mostrar conjuntos (opcional)
    # analizador.mostrar_conjuntos()
    
    exito, arbol = analizador.analizar(tokens)
    
    if exito:
        print("\n" + "="*50)
        print("ÁRBOL SINTÁCTICO:")
        print("="*50)
        arbol.mostrar_arbol()
        return True, arbol
    else:
        return False, None

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
        return False, None, []
    
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    exito, arbol = analizador.analizar(tokens)
    errores = analizador.obtener_errores()
    
    return exito, arbol, errores
