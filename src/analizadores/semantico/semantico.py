# -*- coding: utf-8 -*-
# analizadores/semantico/semantico.py

from typing import List, Optional
from .symtab import ScopedSymTab, ExpType

TIPO_NODOS_DECL = {"int": ExpType.TyInt, "float": ExpType.TyFloat, "bool": ExpType.TyBool}

class SemanticAnalyzer:
    def __init__(self):
        self.ts = ScopedSymTab()
        self.errors: List[str] = []
        self._reported_errors = set()  # Para evitar errores duplicados

    def analyze(self, ast_root):
        if ast_root is None:
            print("[Semántico] AST vacío")
            return
        
        # Limpiar errores reportados al inicio de cada análisis
        self._reported_errors.clear()

        self._visit(ast_root)

        # Imprimir TS en el formato solicitado
        print("\nHASH TABLE:")
        print(self.ts.print_all_custom())
        print()

        if self.errors:
            print("ERRORES SEMÁNTICOS:")
            for e in self.errors:
                print(" -", e)

    # ----------------- Recorrido -----------------

    def _visit(self, node, parent=None):
        if node is None:
            return

        # 1) Declaraciones: nodo 'int'|'float'|'bool' con hijos id
        if node.tipo in TIPO_NODOS_DECL:
            vtype = TIPO_NODOS_DECL[node.tipo]
            for child in getattr(node, "hijos", []):
                if self._es_ident(child):
                    name = child.valor
                    linea = int(child.token_linea or 0)
                    # redeclaración en el scope actual
                    if self.ts.scopes[-1].exists(name):
                        self.errors.append(f"[L{linea}] Redeclaración de '{name}'")
                    # Inserta con valor inicial del tipo
                    self.ts.st_insert(name, linea, vtype)
            # IMPORTANTE: no recorras los hijos id (evita contarlos como uso)
            return

        # 2) Asignación "=": procesa LHS y RHS sin duplicar líneas
        if node.tipo == '=' and len(node.hijos) >= 2:
            lhs = node.hijos[0]
            rhs = node.hijos[1]

            # Solo LHS puede ser id asignable
            if self._es_ident(lhs):
                name = lhs.valor
                linea = int(lhs.token_linea or 0)
                if not self.ts.st_exists(name):
                    self.errors.append(f"[L{linea}] Variable no declarada '{name}'")
                else:
                    lit = self._eval_literal(rhs)
                    if lit is not None:
                        # Si hay literal, actualiza valor y registra la línea UNA sola vez
                        self.ts.st_set_value(name, lit, lineno=linea)
                    else:
                        # Si no hay literal (expresión), cuenta una aparición del id LHS
                        self.ts.st_insert_use(name, linea)

            # Muy importante: visitar SOLO el RHS para detectar ids dentro de la expresión
            self._visit(rhs, node)
            return

        # 3) Nodos cin: marcar variable como modificada
        if node.tipo == 'cin' and node.hijos:
            for child in node.hijos:
                if self._es_ident(child):
                    name = child.valor
                    linea = int(child.token_linea or 0)
                    if not self.ts.st_exists(name):
                        error_key = f"{name}:{linea}"  # Clave única para cada error
                        if error_key not in self._reported_errors:
                            self.errors.append(f"[L{linea}] Variable no declarada '{name}'")
                            self._reported_errors.add(error_key)
                    else:
                        # Solo usamos set_value que ya registra la línea internamente
                        # y establecemos el valor como "input"
                        self.ts.st_set_value(name, "input", lineno=linea)
            return

        # 4) Nodos while/do: procesar condición y cuerpo
        if node.tipo in ('while', 'do'):
            # En nodos while:
            # - El primer hijo es la condición
            # - El segundo hijo es un nodo 'body' que contiene todas las sentencias
            if len(node.hijos) >= 1:
                # Procesar la condición
                self._visit(node.hijos[0], node)
            
            if len(node.hijos) >= 2:
                body_node = node.hijos[1]
                if body_node.tipo == 'body':
                    # Procesar cada sentencia en el cuerpo
                    for stmt in body_node.hijos:
                        self._visit(stmt, node)
            return

        # 4.1) Para do-until/while
        if node.tipo == 'do':
            for child in node.hijos:
                if child.tipo == 'body':
                    # Procesar cada sentencia en el cuerpo del do
                    for stmt in child.hijos:
                        if stmt.tipo == 'while':
                            # Procesar el while anidado
                            if len(stmt.hijos) >= 1:
                                # Procesar la condición del while
                                self._visit(stmt.hijos[0], stmt)
                            if len(stmt.hijos) >= 2 and stmt.hijos[1].tipo == 'body':
                                # Procesar el cuerpo del while
                                for while_stmt in stmt.hijos[1].hijos:
                                    self._visit(while_stmt, stmt)
                        else:
                            # Procesar otras sentencias en el do
                            self._visit(stmt, node)
                elif child.tipo in ('while', 'until'):
                    # Procesar la condición del until/while final
                    if child.hijos:
                        self._visit(child.hijos[0], node)
            return

        # 5) Nodos cout: verificar variables en expresiones
        if node.tipo == 'cout':
            # Procesar cada expresión a imprimir
            for child in node.hijos:
                self._visit(child, node)
            return

        # 6) Uso de identificadores (no LHS en declaración ni ya manejado en '=')
        if self._es_ident(node):
            name = node.valor
            linea = int(node.token_linea or 0)
            if not self.ts.st_exists(name):
                error_key = f"{name}:{linea}"  # Clave única para cada error
                if error_key not in self._reported_errors:
                    self.errors.append(f"[L{linea}] Variable no declarada '{name}'")
                    self._reported_errors.add(error_key)
            else:
                self.ts.st_insert_use(name, linea)
            return

        # Recorre hijos
        for ch in getattr(node, "hijos", []):
            self._visit(ch, node)

    # ----------------- Helpers -----------------

    def _es_ident(self, node) -> bool:
        return (
            getattr(node, "tipo", "") == "id" or
            getattr(node, "token_tipo", "") == "Identificador"
        )

    def _eval_literal(self, node) -> Optional[object]:
        """Devuelve int/float/string/bool si 'node' es literal; de lo contrario, None."""
        if node is None:
            return None

        if node.tipo == "numero":
            try:
                lex = str(node.valor)
                if any(c in lex for c in ".eE"):
                    return float(lex)
                else:
                    return int(lex)
            except Exception:
                return None

        if node.tipo == "cadena":
            val = str(node.valor)
            if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
                return val[1:-1]
            return val

        if node.tipo == "booleano":
            return True if str(node.valor).lower() == "true" else False

        # Si RHS es paréntesis/unario con literal, intenta bajar
        if getattr(node, "hijos", None):
            if len(node.hijos) == 1:
                return self._eval_literal(node.hijos[0])

        return None
