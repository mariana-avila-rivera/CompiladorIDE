# -*- coding: utf-8 -*-
"""
Árbol Semántico con evaluación de expresiones - Vista de Tabla TreeView
"""

import tkinter as tk
from tkinter import ttk

class NodoSemantico:
    """Nodo del árbol semántico con valor evaluado"""
    def __init__(self, tipo, valor, valor_evaluado=None, token_tipo='', token_linea='', token_columna='', tiene_error=False):
        self.tipo = tipo
        self.valor = valor
        self.valor_evaluado = valor_evaluado
        self.token_tipo = token_tipo
        self.token_linea = token_linea
        self.token_columna = token_columna
        self.tiene_error = tiene_error  # Marca si el nodo tiene error semántico
        self.hijos = []
    
    def agregar_hijo(self, hijo):
        if hijo:
            self.hijos.append(hijo)
            # Si el hijo tiene error, el padre también
            if getattr(hijo, 'tiene_error', False):
                self.tiene_error = True
    
    def __repr__(self):
        if self.tiene_error:
            return f"{self.valor} (ERROR)"
        if self.valor_evaluado is not None:
            if isinstance(self.valor_evaluado, bool):
                val_str = "true" if self.valor_evaluado else "false"
            elif isinstance(self.valor_evaluado, float):
                val_str = f"{self.valor_evaluado:.2f}"
            else:
                val_str = str(self.valor_evaluado)
            return f"{self.valor} ({val_str})"
        return str(self.valor)


class SemanticTreeWidget(tk.Frame):
    """Widget tipo TreeView para mostrar el árbol semántico con valores evaluados"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        """Crea el TreeView y scrollbars"""
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # TreeView con columnas
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("tipo", "linea", "columna"),
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='browse'
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("#0", text="Estructura del Programa", anchor=tk.W)
        self.tree.heading("tipo", text="Tipo de token", anchor=tk.W)
        self.tree.heading("linea", text="Línea", anchor=tk.W)
        self.tree.heading("columna", text="Columna", anchor=tk.W)
        
        self.tree.column("#0", width=400, minwidth=200, stretch=True)
        self.tree.column("tipo", width=150, minwidth=100, stretch=True)
        self.tree.column("linea", width=80, minwidth=50, stretch=False)
        self.tree.column("columna", width=80, minwidth=50, stretch=False)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Estilo
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Segoe UI', 9))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
    
    def mostrar_arbol(self, raiz):
        """Muestra el árbol semántico en el TreeView"""
        print(f"[SemanticTreeWidget] Mostrando árbol en TreeView")
        
        # Limpiar árbol anterior
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not raiz:
            print("[SemanticTreeWidget] No hay árbol para mostrar")
            return
        
        # Insertar nodos recursivamente
        self._insertar_nodo(raiz, "")
        
        print(f"[SemanticTreeWidget] Árbol mostrado en TreeView")
    
    def _insertar_nodo(self, nodo, parent_id):
        """Inserta un nodo y sus hijos recursivamente en el TreeView"""
        if not nodo:
            return
        
        # Texto a mostrar (con valor evaluado si existe)
        texto = self._formato_texto(nodo)
        
        # Tipo de token: si tiene error, marcar como ERROR
        if getattr(nodo, 'tiene_error', False):
            tipo_token = 'ERROR'
        else:
            tipo_token = getattr(nodo, 'token_tipo', '') or ''
        
        # Línea y columna
        linea = getattr(nodo, 'token_linea', '') or ''
        columna = getattr(nodo, 'token_columna', '') or ''
        
        # Insertar el nodo
        node_id = self.tree.insert(
            parent_id,
            'end',
            text=texto,
            values=(tipo_token, linea, columna),
            open=True  # Expandido por defecto
        )
        
        # Insertar hijos
        for hijo in getattr(nodo, 'hijos', []):
            if hijo:
                self._insertar_nodo(hijo, node_id)
    
    def _formato_texto(self, nodo):
        """Formatea el texto del nodo con valor evaluado"""
        valor_base = str(nodo.valor)
        
        # Si tiene error, no mostrar valor evaluado
        if getattr(nodo, 'tiene_error', False):
            return valor_base
        
        # Si tiene valor evaluado, agregarlo entre paréntesis
        if nodo.valor_evaluado is not None:
            if isinstance(nodo.valor_evaluado, bool):
                val_str = "true" if nodo.valor_evaluado else "false"
            elif isinstance(nodo.valor_evaluado, float):
                val_str = f"{nodo.valor_evaluado:.2f}"
            elif isinstance(nodo.valor_evaluado, int):
                val_str = str(nodo.valor_evaluado)
            else:
                val_str = str(nodo.valor_evaluado)
            
            return f"{valor_base} ({val_str})"
        
        return valor_base
    
    def limpiar(self):
        """Limpia el TreeView"""
        for item in self.tree.get_children():
            self.tree.delete(item)


class SemanticTreeBuilder:
    """Construye el árbol semántico con evaluación de expresiones"""
    
    def __init__(self, symbol_table, errores_semanticos=None):
        self.symtab = symbol_table
        self.errores_semanticos = errores_semanticos or []
        print(f"[SemanticTreeBuilder] Inicializado con {len(self.errores_semanticos)} errores semánticos")
        
        # ELIMINADO: No inicializar variables aquí
        # La inicialización ya la hizo el SemanticAnalyzer
    
    def construir(self, ast_root):
        """Construye el árbol semántico desde el AST"""
        print(f"[SemanticTreeBuilder] Construyendo árbol semántico")
        if not ast_root:
            return None
        
        resultado = self._procesar_nodo(ast_root)
        print(f"[SemanticTreeBuilder] Árbol semántico construido")
        return resultado
    
    def _tiene_error_en_posicion(self, linea, columna):
        """Verifica si hay un error semántico en la posición dada"""
        for error in self.errores_semanticos:
            if error.get('linea') == linea and error.get('columna') == columna:
                return True
        return False
    
    def _procesar_nodo(self, nodo, propagar_error=False):
        """Procesa un nodo del AST y crea el nodo semántico correspondiente"""
        if not nodo:
            return None
        
        tipo = getattr(nodo, 'tipo', '')
        valor = getattr(nodo, 'valor', '')
        token_tipo = getattr(nodo, 'token_tipo', '')
        token_linea = getattr(nodo, 'token_linea', '')
        token_columna = getattr(nodo, 'token_columna', '')
        
        # Verificar si este nodo tiene error
        tiene_error = propagar_error or self._tiene_error_en_posicion(
            int(token_linea) if token_linea else 0,
            int(token_columna) if token_columna else 0
        )
        
        # Programa principal
        if tipo == 'programa':
            sem_nodo = NodoSemantico('programa', 'main', token_tipo=token_tipo, 
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=tiene_error)
            # CLAVE: Procesar hijos directamente SIN crear nodos intermedios
            for hijo in getattr(nodo, 'hijos', []):
                hijo_sem = self._procesar_nodo(hijo, tiene_error)
                if hijo_sem:
                    # Si es una lista (múltiples sentencias/declaraciones), agregar cada una
                    if isinstance(hijo_sem, list):
                        for item in hijo_sem:
                            if item:
                                sem_nodo.agregar_hijo(item)
                    else:
                        sem_nodo.agregar_hijo(hijo_sem)
            return sem_nodo
        
        # Declaraciones: MOSTRAR valores iniciales (0, 0.0, false)
        if tipo in ('int', 'float', 'bool'):
            sem_nodo = NodoSemantico('declaracion', tipo, token_tipo=token_tipo,
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=tiene_error)
            for hijo in getattr(nodo, 'hijos', []):
                if getattr(hijo, 'tipo', '') == 'id':
                    # MOSTRAR el valor inicial según el tipo
                    if not tiene_error:
                        if tipo == 'int':
                            id_valor = 0
                        elif tipo == 'float':
                            id_valor = 0.0
                        elif tipo == 'bool':
                            id_valor = False
                        else:
                            id_valor = None
                    else:
                        id_valor = None
                    
                    id_error = tiene_error or self._tiene_error_en_posicion(
                        int(getattr(hijo, 'token_linea', 0) or 0),
                        int(getattr(hijo, 'token_columna', 0) or 0)
                    )
                    id_sem = NodoSemantico('id', hijo.valor, 
                                          valor_evaluado=id_valor,
                                          token_tipo=getattr(hijo, 'token_tipo', ''),
                                          token_linea=getattr(hijo, 'token_linea', ''),
                                          token_columna=getattr(hijo, 'token_columna', ''),
                                          tiene_error=id_error)
                    sem_nodo.agregar_hijo(id_sem)
            return sem_nodo
        
        # Asignaciones: PRIMERO evaluar/procesar, LUEGO actualizar tabla
        if tipo == '=':
            hijos = getattr(nodo, 'hijos', [])
            if len(hijos) >= 2:
                id_nodo = hijos[0]
                expr_nodo = hijos[1]
                
                id_name = getattr(id_nodo, 'valor', '')
                
                # PASO 1: Evaluar la expresión con valores ACTUALES (antes de actualizar)
                valor_calculado = None if tiene_error else self._evaluar_expresion(expr_nodo)
                print(f"[SemanticTreeBuilder] Evaluada expresión para '{id_name}': {valor_calculado}")
                
                # PASO 2: Procesar la expresión para el árbol visual (también usa valores actuales)
                expr_sem = self._procesar_expresion(expr_nodo, tiene_error)
                
                # PASO 3: AHORA SÍ actualizar la tabla de símbolos con el nuevo valor
                if not tiene_error and valor_calculado is not None and self.symtab and self.symtab.st_exists(id_name):
                    valor_viejo = self._obtener_valor_variable(id_name)
                    linea = int(getattr(id_nodo, 'token_linea', 0) or 0)
                    self.symtab.st_set_value(id_name, valor_calculado, lineno=linea)
                    print(f"[SemanticTreeBuilder] Variable '{id_name}' actualizada de {valor_viejo} a {valor_calculado}")
                
                sem_nodo = NodoSemantico('asignacion', '=', valor_evaluado=valor_calculado,
                                        token_tipo=token_tipo, token_linea=token_linea, 
                                        token_columna=token_columna, tiene_error=tiene_error)
                
                # ID como hijo - MOSTRAR EL VALOR NUEVO (el calculado)
                id_error = tiene_error or self._tiene_error_en_posicion(
                    int(getattr(id_nodo, 'token_linea', 0) or 0),
                    int(getattr(id_nodo, 'token_columna', 0) or 0)
                )
                id_sem = NodoSemantico('id', id_name, 
                                      valor_evaluado=None if id_error else valor_calculado,
                                      token_tipo=getattr(id_nodo, 'token_tipo', ''),
                                      token_linea=getattr(id_nodo, 'token_linea', ''),
                                      token_columna=getattr(id_nodo, 'token_columna', ''),
                                      tiene_error=id_error)
                sem_nodo.agregar_hijo(id_sem)
                
                # Agregar la expresión procesada (ya calculada antes)
                if expr_sem:
                    sem_nodo.agregar_hijo(expr_sem)
                return sem_nodo
        
        # Control de flujo
        if tipo == 'if':
            return self._procesar_if(nodo, tiene_error)
        
        if tipo == 'while':
            return self._procesar_while(nodo, tiene_error)
        
        if tipo == 'do':
            return self._procesar_do(nodo, tiene_error)
        
        # I/O
        if tipo == 'cin':
            sem_nodo = NodoSemantico('entrada', 'cin', token_tipo=token_tipo,
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=tiene_error)
            for hijo in getattr(nodo, 'hijos', []):
                if getattr(hijo, 'tipo', '') == 'id':
                    id_error = tiene_error or self._tiene_error_en_posicion(
                        int(getattr(hijo, 'token_linea', 0) or 0),
                        int(getattr(hijo, 'token_columna', 0) or 0)
                    )
                    id_sem = NodoSemantico('id', hijo.valor,
                                          token_tipo=getattr(hijo, 'token_tipo', ''),
                                          token_linea=getattr(hijo, 'token_linea', ''),
                                          token_columna=getattr(hijo, 'token_columna', ''),
                                          tiene_error=id_error)
                    sem_nodo.agregar_hijo(id_sem)
            return sem_nodo
        
        if tipo == 'cout':
            sem_nodo = NodoSemantico('salida', 'cout', token_tipo=token_tipo,
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=tiene_error)
            for hijo in getattr(nodo, 'hijos', []):
                hijo_sem = self._procesar_expresion(hijo, tiene_error)
                if hijo_sem:
                    sem_nodo.agregar_hijo(hijo_sem)
            return sem_nodo
        
        # Por defecto: SALTAR nodos contenedores innecesarios
        # SOLO procesar hijos si el nodo es un contenedor sin significado semántico
        if tipo in ('lista_declaracion', 'declaracion', 'sentencia', 'lista_sentencias'):
            # Estos son nodos de la gramática que NO deben aparecer en el árbol semántico
            # Procesar sus hijos directamente
            result = []
            for hijo in getattr(nodo, 'hijos', []):
                hijo_sem = self._procesar_nodo(hijo, tiene_error)
                if hijo_sem:
                    if isinstance(hijo_sem, list):
                        result.extend(hijo_sem)
                    else:
                        result.append(hijo_sem)
            # Si solo hay un elemento, devolverlo directamente
            if len(result) == 1:
                return result[0]
            # Si hay múltiples, devolver la lista
            return result if result else None
        
        # Otros nodos desconocidos
        sem_nodo = NodoSemantico(tipo, valor, token_tipo=token_tipo,
                                token_linea=token_linea, token_columna=token_columna,
                                tiene_error=tiene_error)
        for hijo in getattr(nodo, 'hijos', []):
            hijo_sem = self._procesar_nodo(hijo, tiene_error)
            if hijo_sem:
                if isinstance(hijo_sem, list):
                    for item in hijo_sem:
                        if item:
                            sem_nodo.agregar_hijo(item)
                else:
                    sem_nodo.agregar_hijo(hijo_sem)
        return sem_nodo
    
    def _procesar_expresion(self, nodo, tiene_error_padre=False):
        """Procesa una expresión COMPLETA, evaluando y propagando valores - RECURSIVAMENTE"""
        if not nodo:
            return None
        
        tipo = getattr(nodo, 'tipo', '')
        valor = getattr(nodo, 'valor', '')
        token_tipo = getattr(nodo, 'token_tipo', '')
        token_linea = getattr(nodo, 'token_linea', '')
        token_columna = getattr(nodo, 'token_columna', '')
        
        # Verificar error en este nodo
        tiene_error = tiene_error_padre or self._tiene_error_en_posicion(
            int(token_linea) if token_linea else 0,
            int(token_columna) if token_columna else 0
        )
        
        print(f"[_procesar_expresion] tipo={tipo}, valor={valor}, hijos={len(getattr(nodo, 'hijos', []))}")
        
        # Literales: devolver con su valor
        if tipo == 'numero':
            try:
                val = None if tiene_error else (float(valor) if '.' in str(valor) else int(valor))
                print(f"[_procesar_expresion] Literal número: {valor} = {val}")
                return NodoSemantico('numero', valor, valor_evaluado=val,
                                    token_tipo=token_tipo, token_linea=token_linea, 
                                    token_columna=token_columna, tiene_error=tiene_error)
            except:
                return NodoSemantico('numero', valor, token_tipo=token_tipo,
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=True)
        
        if tipo == 'cadena':
            val = None if tiene_error else valor
            return NodoSemantico('cadena', valor, valor_evaluado=val,
                                token_tipo=token_tipo, token_linea=token_linea, 
                                token_columna=token_columna, tiene_error=tiene_error)
        
        if tipo == 'booleano':
            val = None if tiene_error else (valor.lower() == 'true')
            return NodoSemantico('booleano', valor, valor_evaluado=val,
                                token_tipo=token_tipo, token_linea=token_linea, 
                                token_columna=token_columna, tiene_error=tiene_error)
        
        if tipo == 'id':
            val = None if tiene_error else self._obtener_valor_variable(valor)
            print(f"[_procesar_expresion] Variable {valor} = {val}")
            return NodoSemantico('id', valor, valor_evaluado=val,
                                token_tipo=token_tipo, token_linea=token_linea, 
                                token_columna=token_columna, tiene_error=tiene_error)
        
        # CLAVE: Detectar si es un OPERADOR (no por tipo, sino por valor)
        # Los operadores ya vienen en el AST con su valor correcto
        if valor in ('+', '-', '*', '/', '%', '^', '<', '<=', '>', '>=', '==', '!=', '&&', '||', '!'):
            print(f"[_procesar_expresion] Procesando operador: {valor}")
            
            # Evaluar el resultado SOLO si no hay error
            valor_calculado = None if tiene_error else self._evaluar_expresion(nodo)
            print(f"[_procesar_expresion] Resultado del operador {valor}: {valor_calculado}")
            
            # Crear nodo del operador con su resultado
            sem_nodo = NodoSemantico('operador', valor, valor_evaluado=valor_calculado,
                                    token_tipo=token_tipo, token_linea=token_linea, 
                                    token_columna=token_columna, tiene_error=tiene_error)
            
            # PROCESAR CADA HIJO RECURSIVAMENTE - esto creará el desglose completo
            hijos = getattr(nodo, 'hijos', [])
            print(f"[_procesar_expresion] Operador {valor} tiene {len(hijos)} hijos")
            for idx, hijo in enumerate(hijos):
                print(f"[_procesar_expresion] Procesando hijo {idx+1}/{len(hijos)} del operador {valor}")
                hijo_sem = self._procesar_expresion(hijo, tiene_error)
                if hijo_sem:
                    sem_nodo.agregar_hijo(hijo_sem)
                    print(f"[_procesar_expresion] Hijo {idx+1} agregado: {hijo_sem.valor} = {hijo_sem.valor_evaluado}")
                else:
                    print(f"[_procesar_expresion] ADVERTENCIA: hijo {idx+1} es None")
            
            print(f"[_procesar_expresion] Operador {valor} completado con {len(sem_nodo.hijos)} hijos")
            return sem_nodo
        
        # Si no es literal, operador ni id, pero tiene hijos, procesar recursivamente
        hijos = getattr(nodo, 'hijos', [])
        if hijos:
            print(f"[_procesar_expresion] Nodo contenedor tipo={tipo}, procesando {len(hijos)} hijos")
            # Si solo tiene un hijo, devolver ese hijo procesado
            if len(hijos) == 1:
                return self._procesar_expresion(hijos[0], tiene_error)
            
            # Si tiene múltiples hijos, crear un nodo contenedor
            sem_nodo = NodoSemantico(tipo, valor, token_tipo=token_tipo,
                                    token_linea=token_linea, token_columna=token_columna,
                                    tiene_error=tiene_error)
            for hijo in hijos:
                hijo_sem = self._procesar_expresion(hijo, tiene_error)
                if hijo_sem:
                    sem_nodo.agregar_hijo(hijo_sem)
            return sem_nodo
        
        # Por defecto: nodo sin hijos ni caso especial
        print(f"[_procesar_expresion] Nodo sin procesamiento especial: tipo={tipo}, valor={valor}")
        return NodoSemantico(tipo, valor, token_tipo=token_tipo,
                            token_linea=token_linea, token_columna=token_columna,
                            tiene_error=tiene_error)
    
    def _procesar_if(self, nodo, tiene_error_padre=False):
        """Procesa un nodo if con evaluación de condición"""
        hijos = getattr(nodo, 'hijos', [])
        
        cond_valor = None
        if hijos and not tiene_error_padre:
            cond_valor = self._evaluar_expresion(hijos[0])
        
        sem_nodo = NodoSemantico('if', 'if', valor_evaluado=cond_valor, tiene_error=tiene_error_padre)
        
        # Condición
        if hijos:
            cond_sem = self._procesar_expresion(hijos[0], tiene_error_padre)
            if cond_sem:
                sem_nodo.agregar_hijo(cond_sem)
        
        # Then
        if len(hijos) > 1 and getattr(hijos[1], 'tipo', '') == 'then':
            then_nodo = NodoSemantico('then', 'then', tiene_error=tiene_error_padre)
            for stmt in getattr(hijos[1], 'hijos', []):
                stmt_sem = self._procesar_nodo(stmt, tiene_error_padre)
                if stmt_sem:
                    then_nodo.agregar_hijo(stmt_sem)
            sem_nodo.agregar_hijo(then_nodo)
        
        # Else
        if len(hijos) > 2 and getattr(hijos[2], 'tipo', '') == 'else':
            else_nodo = NodoSemantico('else', 'else', tiene_error=tiene_error_padre)
            for stmt in getattr(hijos[2], 'hijos', []):
                stmt_sem = self._procesar_nodo(stmt, tiene_error_padre)
                if stmt_sem:
                    else_nodo.agregar_hijo(stmt_sem)
            sem_nodo.agregar_hijo(else_nodo)
        
        return sem_nodo
    
    def _procesar_while(self, nodo, tiene_error_padre=False):
        """Procesa un nodo while"""
        hijos = getattr(nodo, 'hijos', [])
        
        cond_valor = None
        if hijos and not tiene_error_padre:
            cond_valor = self._evaluar_expresion(hijos[0])
        
        sem_nodo = NodoSemantico('while', 'while', valor_evaluado=cond_valor, tiene_error=tiene_error_padre)
        
        # Condición
        if hijos:
            cond_sem = self._procesar_expresion(hijos[0], tiene_error_padre)
            if cond_sem:
                sem_nodo.agregar_hijo(cond_sem)
        
        # Cuerpo
        if len(hijos) > 1 and getattr(hijos[1], 'tipo', '') == 'body':
            body_nodo = NodoSemantico('body', 'cuerpo', tiene_error=tiene_error_padre)
            for stmt in getattr(hijos[1], 'hijos', []):
                stmt_sem = self._procesar_nodo(stmt, tiene_error_padre)
                if stmt_sem:
                    body_nodo.agregar_hijo(stmt_sem)
            sem_nodo.agregar_hijo(body_nodo)
        
        return sem_nodo
    
    def _procesar_do(self, nodo, tiene_error_padre=False):
        """Procesa un nodo do-until/while"""
        hijos = getattr(nodo, 'hijos', [])
        sem_nodo = NodoSemantico('do', 'do', tiene_error=tiene_error_padre)
        
        # Cuerpo
        if hijos and getattr(hijos[0], 'tipo', '') == 'body':
            body_nodo = NodoSemantico('body', 'cuerpo', tiene_error=tiene_error_padre)
            for stmt in getattr(hijos[0], 'hijos', []):
                stmt_sem = self._procesar_nodo(stmt, tiene_error_padre)
                if stmt_sem:
                    body_nodo.agregar_hijo(stmt_sem)
            sem_nodo.agregar_hijo(body_nodo)
        
        # Until/While
        if len(hijos) > 1:
            cond_nodo = hijos[1]
            cond_tipo = getattr(cond_nodo, 'tipo', '')
            if cond_tipo in ('until', 'while'):
                cond_hijos = getattr(cond_nodo, 'hijos', [])
                cond_valor = None if tiene_error_padre else (self._evaluar_expresion(cond_hijos[0]) if cond_hijos else None)
                
                cond_sem = NodoSemantico(cond_tipo, cond_tipo, valor_evaluado=cond_valor, tiene_error=tiene_error_padre)
                if cond_hijos:
                    expr_sem = self._procesar_expresion(cond_hijos[0], tiene_error_padre)
                    if expr_sem:
                        cond_sem.agregar_hijo(expr_sem)
                sem_nodo.agregar_hijo(cond_sem)
        
        return sem_nodo
    
    def _evaluar_expresion(self, nodo):
        """Evalúa una expresión recursivamente y devuelve su valor numérico/booleano"""
        if not nodo:
            return None
        
        tipo = getattr(nodo, 'tipo', '')
        valor = getattr(nodo, 'valor', '')
        
        print(f"[_evaluar_expresion] Evaluando: tipo={tipo}, valor={valor}")
        
        # Literales
        if tipo == 'numero':
            try:
                resultado = float(valor) if '.' in str(valor) else int(valor)
                print(f"[_evaluar_expresion] Número: {valor} = {resultado}")
                return resultado
            except:
                return None
        
        if tipo == 'booleano':
            resultado = valor.lower() == 'true'
            print(f"[_evaluar_expresion] Booleano: {valor} = {resultado}")
            return resultado
        
        if tipo == 'cadena':
            print(f"[_evaluar_expresion] Cadena: {valor}")
            return valor
        
        if tipo == 'id':
            resultado = self._obtener_valor_variable(valor)
            print(f"[_evaluar_expresion] Variable {valor} = {resultado}")
            return resultado
        
        # Operadores: CLAVE - evaluar por el VALOR del nodo, no por el tipo
        hijos = getattr(nodo, 'hijos', [])
        
        # Operadores binarios aritméticos
        if valor in ('+', '-', '*', '/', '%', '^'):
            if len(hijos) >= 2:
                izq = self._evaluar_expresion(hijos[0])
                der = self._evaluar_expresion(hijos[1])
                
                print(f"[_evaluar_expresion] Operador {valor}: izq={izq}, der={der}")
                
                if izq is not None and der is not None:
                    try:
                        resultado = None
                        if valor == '+': resultado = izq + der
                        elif valor == '-': resultado = izq - der
                        elif valor == '*': resultado = izq * der
                        elif valor == '/': resultado = izq / der if der != 0 else None
                        elif valor == '%': resultado = izq % der if der != 0 else None
                        elif valor == '^': resultado = izq ** der
                        
                        print(f"[_evaluar_expresion] Resultado: {izq} {valor} {der} = {resultado}")
                        return resultado
                    except Exception as e:
                        print(f"[_evaluar_expresion] Error en operación: {e}")
                        return None
                else:
                    print(f"[_evaluar_expresion] Operandos None: izq={izq}, der={der}")
            else:
                print(f"[_evaluar_expresion] Operador {valor} con {len(hijos)} hijos (se esperaban 2)")
        
        # Operadores relacionales
        if valor in ('<', '<=', '>', '>=', '==', '!='):
            if len(hijos) >= 2:
                izq = self._evaluar_expresion(hijos[0])
                der = self._evaluar_expresion(hijos[1])
                
                if izq is not None and der is not None:
                    try:
                        if valor == '<': return izq < der
                        elif valor == '<=': return izq <= der
                        elif valor == '>': return izq > der
                        elif valor == '>=': return izq >= der
                        elif valor == '==': return izq == der
                        elif valor == '!=': return izq != der
                    except:
                        return None
        
        # Operadores lógicos
        if valor == '!':
            if hijos:
                val = self._evaluar_expresion(hijos[0])
                return not val if val is not None else None
        
        if valor in ('&&', 'and'):
            if len(hijos) >= 2:
                izq = self._evaluar_expresion(hijos[0])
                der = self._evaluar_expresion(hijos[1])
                return izq and der if izq is not None and der is not None else None
        
        if valor in ('||', 'or'):
            if len(hijos) >= 2:
                izq = self._evaluar_expresion(hijos[0])
                der = self._evaluar_expresion(hijos[1])
                return izq or der if izq is not None and der is not None else None
        
        # Si el nodo tiene un solo hijo, evaluar ese hijo
        if len(hijos) == 1:
            print(f"[_evaluar_expresion] Nodo con un hijo, evaluando recursivamente")
            return self._evaluar_expresion(hijos[0])
        
        print(f"[_evaluar_expresion] No se pudo evaluar: tipo={tipo}, valor={valor}")
        return None
    
    def _obtener_valor_variable(self, nombre):
        """Obtiene el valor ACTUAL de una variable desde la tabla de símbolos"""
        if not self.symtab or not self.symtab.st_exists(nombre):
            print(f"[_obtener_valor_variable] Variable '{nombre}' no existe en tabla")
            return None
        
        # Buscar en todos los scopes (del más interno al más externo)
        for tab in reversed(self.symtab.scopes):
            bucket = tab._find(nombre)
            if bucket:
                val = bucket.last_value
                
                # Manejar casos especiales
                if val == "input" or val == "<input>":
                    print(f"[_obtener_valor_variable] Variable '{nombre}' tiene valor <input>, retornando None")
                    return None
                
                # Si el valor es 0, 0.0, False (valores por defecto), verificar si la variable
                # ha sido asignada realmente o solo declarada
                if val in (0, 0.0, False, "") and len(bucket.lines) == 1:
                    # Solo tiene una línea (la declaración), no ha sido asignada
                    print(f"[_obtener_valor_variable] Variable '{nombre}' solo declarada, retornando valor inicial {val}")
                    return val
                
                # Retornar el valor actual
                print(f"[_obtener_valor_variable] Variable '{nombre}' = {val} (tipo: {type(val).__name__})")
                return val
        
        print(f"[_obtener_valor_variable] Variable '{nombre}' no encontrada en ningún scope")
        return None
