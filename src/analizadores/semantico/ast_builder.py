# -*- coding: utf-8 -*-
"""
AST Builder para la fase Semántica.
- Normaliza terminales (id, numero, cadena, booleano).
- Ajusta nodos según la gramática extendida.
- Transforma ++/-- en asignaciones.
- CONSTRUYE CORRECTAMENTE EXPRESIONES ANIDADAS
"""

from typing import List, Optional
from analizadores.sintactico.ast_builder import NodoAST

# Precedencia: menor número = menor precedencia
_PRECEDENCIA = {
    '||': 0, 'or': 0,
    '&&': 1, 'and': 1,
    '==': 2, '!=': 2, '<': 2, '<=': 2, '>': 2, '>=': 2,
    '+': 3, '-': 3,
    '*': 4, '/': 4, '%': 4,
    '^': 5
}

_SIMBOLOS_OMITIR = {'(', ')', ',', ';', '{', '}', '[', ']', '<<', '>>', 'ε'}


class SemanticASTBuilder:
    """
    Convierte el árbol sintáctico (NodoArbol) en un AST normalizado para Semántico.
    """

    def construir_ast(self, arbol_sintactico):
        if not arbol_sintactico:
            return None
        raiz = self._proc(arbol_sintactico)

        # Siempre devolvemos un único nodo
        if isinstance(raiz, list):
            prog = NodoAST(tipo="programa", valor="programa")
            for h in raiz:
                if h:
                    prog.agregar_hijo(h)
            return prog
        return raiz

    # ----------------- Procesadores -----------------

    def _proc(self, n):
        if not n:
            return None

        v = self._get_val(n)
        if v in _SIMBOLOS_OMITIR:
            return None

        hijos = getattr(n, 'hijos', [])

        # programa → main { lista_declaracion } ;
        if v == 'programa':
            prog = NodoAST(tipo='programa', valor='programa')
            for h in hijos:
                hv = self._get_val(h)
                if hv in _SIMBOLOS_OMITIR or hv == 'main':
                    continue
                ph = self._proc(h)
                if ph:
                    if isinstance(ph, list):
                        for x in ph: prog.agregar_hijo(x)
                    else:
                        prog.agregar_hijo(ph)
            return prog

        # Declaraciones: declaracion_variable → tipo lista_identificadores ;
        if v == 'declaracion_variable' and len(hijos) >= 2:
            tipo = self._proc(hijos[0])             # nodo 'int'/'float'/'bool'
            idlist = self._flatten(self._proc(hijos[1]))
            if not tipo:
                return idlist
            # tipo como raíz, ids como hijos
            for ident in idlist:
                if ident: tipo.agregar_hijo(ident)
            return tipo

        # tipo → int|float|bool  (raíz con su lexema)
        if v == 'tipo' and hijos:
            t = self._proc(hijos[0])
            if isinstance(t, NodoAST):
                return NodoAST(tipo=t.valor, valor=t.valor,
                                token_tipo=t.token_tipo, token_linea=t.token_linea, token_columna=t.token_columna)
            return t

        # lista_identificadores → id lista_identificadores_aux
        if v in ('lista_identificadores', 'lista_identificadores_aux'):
            lst = []
            for h in hijos:
                ph = self._proc(h)
                if not ph: continue
                if isinstance(ph, list): lst.extend(ph)
                else: lst.append(ph)
            # Filtra sólo nodos id
            lst = [x for x in lst if isinstance(x, NodoAST) and x.tipo == 'id']
            return lst

        # Asignación: asignacion → id asignacion_op
        if v == 'asignacion' and len(hijos) >= 2:
            idn = self._proc(hijos[0])   # id (normalizado)
            opn = hijos[1]
            # asignacion_op -> '++'| '--' | '=' expresion ';'
            op_children = getattr(opn, 'hijos', [])
            if not op_children:
                return None
            op_val = self._get_val(op_children[0])

            if op_val in ('++', '--'):
                # id = id +/- 1
                return self._mk_incdec(idn, '+' if op_val == '++' else '-')
            else:
                # '=' expresion
                asign = NodoAST(tipo='=', valor='=')
                asign.agregar_hijo(idn)
                if len(op_children) > 1:
                    # CLAVE: Procesar la expresión correctamente
                    expr = self._proc_expresion_completa(op_children[1])
                    if expr: asign.agregar_hijo(expr)
                return asign

        # Selección if ( expresion ) then lista_sentencias [else ...] end
        if v == 'seleccion':
            ifn = NodoAST(tipo='if', valor='if')
            # hijos típicos: 'if' '(' expresion ')' 'then' lista_sentencias seleccion_aux
            if len(hijos) >= 6:
                # Procesar condición como expresión
                cond = self._proc_expresion_completa(hijos[2])
                then_body = self._proc(hijos[5])
                if cond: ifn.agregar_hijo(cond)
                then_node = NodoAST(tipo='then', valor='then')
                for s in self._flatten(then_body):
                    then_node.agregar_hijo(s)
                ifn.agregar_hijo(then_node)
                if len(hijos) > 6:
                    aux = self._proc(hijos[6])
                    if aux: ifn.agregar_hijo(aux)
            return ifn

        # seleccion_aux → else lista_sentencias end | end
        if v == 'seleccion_aux':
            if not hijos:
                return None
            hv = self._get_val(hijos[0])
            if hv == 'else':
                els = NodoAST(tipo='else', valor='else')
                if len(hijos) >= 2:
                    body = self._proc(hijos[1])
                    for s in self._flatten(body): els.agregar_hijo(s)
                return els
            # 'end' -> no agrega nodo extra
            return None

        # while ( expresion ) lista_sentencias end
        if v == 'iteracion':
            wn = NodoAST(tipo='while', valor='while')
            if len(hijos) >= 4:
                # Procesar condición como expresión
                cond = self._proc_expresion_completa(hijos[2])
                if cond: 
                    wn.agregar_hijo(cond)
                
                # El cuerpo está después de la condición y antes del 'end'
                # Crear un nodo especial para el cuerpo para mantener la estructura
                body_node = NodoAST(tipo='body', valor='body')
                for i in range(3, len(hijos)):
                    if self._get_val(hijos[i]) == 'end':
                        break
                    body = self._proc(hijos[i])
                    if body:
                        if isinstance(body, list):
                            for stmt in body:
                                if stmt: body_node.agregar_hijo(stmt)
                        else:
                            body_node.agregar_hijo(body)
                
                wn.agregar_hijo(body_node)
            return wn

        # repeticion → do lista_sentencias until ( expresion ) ;
        #            | do lista_sentencias while ( expresion ) lista_sentencias end
        if v == 'repeticion' and len(hijos) >= 3:
            don = NodoAST(tipo='do', valor='do')
            
            # Crear nodo body para el cuerpo principal del do
            body_node = NodoAST(tipo='body', valor='body')
            
            # Procesar la lista de sentencias (puede incluir while anidado)
            body_stmts = self._proc(hijos[1])
            if body_stmts:
                if isinstance(body_stmts, list):
                    for stmt in body_stmts:
                        if stmt:
                            # Si es un while, procésalo como estructura de control
                            if isinstance(stmt, NodoAST) and stmt.tipo == 'while':
                                wn = NodoAST(tipo='while', valor='while')
                                if stmt.hijos:
                                    # La condición del while
                                    cond = stmt.hijos[0]
                                    if cond:
                                        wn.agregar_hijo(cond)
                                    # El cuerpo del while
                                    if len(stmt.hijos) > 1:
                                        while_body = NodoAST(tipo='body', valor='body')
                                        for while_stmt in stmt.hijos[1:]:
                                            if while_stmt:
                                                while_body.agregar_hijo(while_stmt)
                                        wn.agregar_hijo(while_body)
                                body_node.agregar_hijo(wn)
                            else:
                                body_node.agregar_hijo(stmt)
                else:
                    body_node.agregar_hijo(body_stmts)
            
            don.agregar_hijo(body_node)
            
            # Procesar la parte until/while
            kw = self._get_val(hijos[2])
            if kw == 'until':
                # Asegurarse de procesar la expresión completa del until
                un = NodoAST(tipo='until', valor='until')
                # Buscar la expresión después del paréntesis
                for i in range(4, len(hijos)):
                    if self._get_val(hijos[i]) != ')':  # Ignorar el paréntesis
                        cond = self._proc(hijos[i])
                        if cond:
                            un.agregar_hijo(cond)
                don.agregar_hijo(un)
            elif kw == 'while':
                cond = self._proc(hijos[4]) if len(hijos) > 4 else None
                wn = NodoAST(tipo='while', valor='while')
                if cond: wn.agregar_hijo(cond)
                # bloque extra después de while
                extra = self._proc(hijos[5]) if len(hijos) > 5 else None
                if extra:
                    block = NodoAST(tipo='body', valor='body')
                    for s in self._flatten(extra): block.agregar_hijo(s)
                    wn.agregar_hijo(block)
                don.agregar_hijo(wn)
            
            return don

        # cout << lista_salida ;
        if v == 'sent_out':
            cn = NodoAST(tipo='cout', valor='cout')
            for h in hijos[1:]:
                ph = self._proc(h)
                for e in self._flatten(ph):
                    if e and self._get_val(e) not in _SIMBOLOS_OMITIR:
                        cn.agregar_hijo(e)
            return cn

        # cin >> id ;
        if v == 'sent_in':
            cin = NodoAST(tipo='cin', valor='cin')
            for h in hijos[1:]:
                ph = self._proc(h)
                for e in self._flatten(ph):
                    if e and isinstance(e, NodoAST) and e.tipo == 'id':
                        cin.agregar_hijo(e)
            return cin

        # lista_sentencias: sólo aplana
        if v in ('lista_sentencias', 'lista_salida', 'lista_salida_aux'):
            ret = []
            for h in hijos:
                ph = self._proc(h)
                if not ph: continue
                if isinstance(ph, list): ret.extend(ph)
                else: ret.append(ph)
            return ret

        # ELIMINADO: No reorganizar expresiones aquí, usar _proc_expresion_completa
        # Expresiones se procesan con el nuevo método

        if v in ('suma_op', 'operador_termino', 'mult_op', 'rel_op', 'asignacion_op'):
            planos = []
            for h in hijos:
                ph = self._proc(h)
                if ph is None: continue
                if isinstance(ph, list): planos.extend(ph)
                else: planos.append(ph)
            # devuelve el primer token operador (nodo AST)
            for p in planos:
                if isinstance(p, NodoAST) and p.valor in _PRECEDENCIA or p.valor in ('=', '++', '--'):
                    return p
            return planos

        # componente: ( expresion ) | numero | id | booleano | ! componente
        if v == 'componente':
            if len(hijos) == 3 and self._get_val(hijos[0]) == '(' and self._get_val(hijos[2]) == ')':
                # Procesar expresión entre paréntesis
                return self._proc_expresion_completa(hijos[1])
            if len(hijos) == 2 and self._get_val(hijos[0]) == '!':
                op = NodoAST(tipo='!', valor='!')
                rhs = self._proc_expresion_completa(hijos[1])
                if rhs: op.agregar_hijo(rhs)
                return op
            if len(hijos) == 1:
                return self._proc(hijos[0])

        # Terminales
        if not hijos:
            return self._terminal(n)

        # Por defecto
        node = self._terminal(n)
        if node is None:
            node = NodoAST(tipo=v, valor=v)
        for h in hijos:
            ph = self._proc(h)
            if not ph: continue
            if isinstance(ph, list):
                for x in ph:
                    if x: node.agregar_hijo(x)
            else:
                node.agregar_hijo(ph)
        return node

    # ----------------- NUEVO: Procesamiento de expresiones completas -----------------
    
    def _proc_expresion_completa(self, n):
        """
        Procesa una expresión COMPLETA, construyendo correctamente el árbol de operadores.
        Recorre el árbol sintáctico y construye un árbol de expresión con operadores como padres.
        """
        if not n:
            return None
        
        v = self._get_val(n)
        hijos = getattr(n, 'hijos', [])
        
        print(f"[_proc_expresion_completa] Procesando: v={v}, hijos={len(hijos)}")
        
        # Terminales
        if not hijos:
            terminal = self._terminal(n)
            if terminal:
                print(f"[_proc_expresion_completa] Terminal: {terminal.valor}")
            return terminal
        
        # CASOS ESPECIALES que NO deben recolectar elementos
        
        # Paréntesis: extraer la expresión interna directamente
        if v == 'componente' and len(hijos) == 3:
            if self._get_val(hijos[0]) == '(' and self._get_val(hijos[2]) == ')':
                print(f"[_proc_expresion_completa] Paréntesis detectados, procesando expresión interna")
                return self._proc_expresion_completa(hijos[1])
        
        # Operador unario !
        if v == 'componente' and len(hijos) == 2:
            if self._get_val(hijos[0]) == '!':
                op = NodoAST(tipo='!', valor='!')
                rhs = self._proc_expresion_completa(hijos[1])
                if rhs:
                    op.agregar_hijo(rhs)
                return op
        
        # RECOLECCIÓN DE ELEMENTOS para construir el árbol
        elementos = []
        
        for h in hijos:
            hv = self._get_val(h)
            
            # Saltar símbolos omitibles
            if hv in _SIMBOLOS_OMITIR:
                continue
            
            # Nodos que son CONTENEDORES de expresiones (NO los procesamos recursivamente,
            # sino que bajamos un nivel)
            if hv in ('expresion', 'expresion_simple', 'expresion_logica', 'expresion_and', 
                      'expresion_relacional', 'termino', 'componente'):
                # Bajar un nivel - procesar el nodo hijo completo
                proc = self._proc_expresion_completa(h)
                if proc:
                    if isinstance(proc, list):
                        elementos.extend(proc)
                    else:
                        elementos.append(proc)
            
            # Nodos AUX: APLANAR COMPLETAMENTE todos los operadores y operandos
            elif hv in ('expresion_simple_aux', 'termino_aux', 'expresion_logica_aux',
                        'expresion_and_aux', 'expresion_relacional_aux'):
                # CLAVE: Aplanar recursivamente TODO el nodo aux
                aux_elementos = self._aplanar_aux(h)
                elementos.extend(aux_elementos)
            
            # Nodos de operador: procesarlos
            elif hv in ('suma_op', 'mult_op', 'rel_op', 'operador_termino'):
                op = self._proc(h)
                if op:
                    if isinstance(op, list):
                        elementos.extend(op)
                    else:
                        elementos.append(op)
            
            else:
                # Otros nodos: procesar normalmente
                proc = self._proc_expresion_completa(h)
                if proc:
                    if isinstance(proc, list):
                        elementos.extend(proc)
                    else:
                        elementos.append(proc)
        
        print(f"[_proc_expresion_completa] Elementos recolectados: {[e.valor if isinstance(e, NodoAST) else str(e) for e in elementos]}")
        
        # Si no hay elementos, retornar None
        if not elementos:
            return None
        
        # Si solo hay un elemento, retornarlo
        if len(elementos) == 1:
            return elementos[0]
        
        # Reorganizar por precedencia
        resultado = self._reorganizar(elementos)
        if resultado:
            print(f"[_proc_expresion_completa] Resultado: {resultado.valor} con {len(resultado.hijos)} hijos")
        else:
            print(f"[_proc_expresion_completa] Resultado: None")
        return resultado
    
    def _aplanar_aux(self, nodo_aux):
        """
        Aplana COMPLETAMENTE un nodo *_aux, extrayendo todos los operadores y operandos
        en orden lineal. 
        
        Estructura típica de *_aux:
        - expresion_simple_aux → suma_op termino expresion_simple_aux
        - termino_aux → operador_termino componente termino_aux
        
        Devuelve una lista plana: [operador1, operando1, operador2, operando2, ...]
        """
        if not nodo_aux:
            return []
        
        hijos = getattr(nodo_aux, 'hijos', [])
        if not hijos:
            # Nodo aux vacío (producción ε)
            return []
        
        elementos = []
        
        # Primer hijo: operador (suma_op, mult_op, rel_op, operador_termino)
        if hijos:
            op_nodo = hijos[0]
            op = self._proc(op_nodo)
            if op:
                if isinstance(op, list):
                    elementos.extend(op)
                else:
                    elementos.append(op)
        
        # Segundo hijo: operando (termino, componente, expresion_simple, etc.)
        if len(hijos) > 1:
            operando_nodo = hijos[1]
            operando = self._proc_expresion_completa(operando_nodo)
            if operando:
                if isinstance(operando, list):
                    elementos.extend(operando)
                else:
                    elementos.append(operando)
        
        # Tercer hijo: siguiente aux (RECURSIVO - aquí está la clave)
        if len(hijos) > 2:
            siguiente_aux = hijos[2]
            # Aplanar recursivamente el siguiente aux
            aux_elementos = self._aplanar_aux(siguiente_aux)
            elementos.extend(aux_elementos)
        
        return elementos

    # ----------------- Utilidades -----------------

    def _terminal(self, n) -> Optional[NodoAST]:
        """Crea un NodoAST terminal normalizado por token."""
        token_info = getattr(n, 'token_info', None)
        val = self._get_val(n)
        if not token_info:
            # no es hoja; devuelve un nodo nominal (o None si símbolo omitible)
            if val in _SIMBOLOS_OMITIR: return None
            return NodoAST(tipo=val, valor=val)

        ttipo = token_info.get('tipo', '')
        tlin = token_info.get('linea', '')
        tcol = token_info.get('columna', '')

        tipo_canon = val
        if ttipo == 'Identificador':
            tipo_canon = 'id'
        elif ttipo in ('Número entero', 'Número real'):
            tipo_canon = 'numero'
        elif ttipo == 'String':
            tipo_canon = 'cadena'
        elif val in ('true', 'false'):
            tipo_canon = 'booleano'

        if val in _SIMBOLOS_OMITIR:
            return None

        return NodoAST(tipo=tipo_canon, valor=val,
                       token_tipo=ttipo, token_linea=tlin, token_columna=tcol)

    def _reorganizar(self, nodos: List[NodoAST]) -> Optional[NodoAST]:
        """Reorganiza expresión (asociatividad izquierda) usando _PRECEDENCIA."""
        nodos = [n for n in nodos if n is not None]
        if not nodos: return None
        if len(nodos) == 1: return nodos[0]

        # buscar operador con menor precedencia de derecha a izquierda
        op_idx = -1
        min_prec = 1e9
        for i in range(len(nodos) - 1, -1, -1):
            n = nodos[i]
            if not isinstance(n, NodoAST): continue
            if n.valor in _PRECEDENCIA and len(n.hijos) == 0:
                p = _PRECEDENCIA[n.valor]
                if p < min_prec:
                    min_prec = p
                    op_idx = i
        if op_idx == -1:
            return nodos[0]

        op = nodos[op_idx]
        left = nodos[:op_idx]
        right = nodos[op_idx + 1:]
        op.hijos = []
        if left:
            l = self._reorganizar(left)
            if l: op.agregar_hijo(l)
        if right:
            r = self._reorganizar(right)
            if r: op.agregar_hijo(r)
        return op

    def _mk_incdec(self, id_node: NodoAST, sign: str) -> NodoAST:
        """id = id +/- 1"""
        asign = NodoAST(tipo='=', valor='=')
        asign.agregar_hijo(id_node)
        op = NodoAST(tipo=sign, valor=sign)
        # copia del id para RHS
        id2 = NodoAST(tipo=id_node.tipo, valor=id_node.valor,
                      token_tipo=id_node.token_tipo, token_linea=id_node.token_linea, token_columna=id_node.token_columna)
        uno = NodoAST(tipo='numero', valor='1')
        op.agregar_hijo(id2)
        op.agregar_hijo(uno)
        asign.agregar_hijo(op)
        return asign

    def _flatten(self, x):
        if x is None: return []
        if isinstance(x, list): return x
        return [x]

    def _get_val(self, n):
        return getattr(n, 'valor', getattr(n, 'tipo', str(n)))
