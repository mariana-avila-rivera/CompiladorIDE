# -*- coding: utf-8 -*-
# analizadores/semantico/semantico.py

from typing import List, Optional, Tuple
from .symtab import ScopedSymTab, ExpType
from analizadores.sintactico.ast_builder import NodoAST

TIPO_NODOS_DECL = {"int": ExpType.TyInt, "float": ExpType.TyFloat, "bool": ExpType.TyBool}

def _is_numeric(t: str) -> bool:
    return t in (ExpType.TyInt, ExpType.TyFloat)

def _is_integer(t: str) -> bool:
    return t == ExpType.TyInt

def _promote(a: str, b: str) -> str:
    if ExpType.TyError in (a, b): return ExpType.TyError
    if a == b: return a
    if _is_numeric(a) and _is_numeric(b): return ExpType.TyFloat
    return ExpType.TyError

def _assignable(dst: str, src: str) -> bool:
    if dst == ExpType.TyFloat and src in (ExpType.TyInt, ExpType.TyFloat): return True
    if dst == ExpType.TyInt and src == ExpType.TyInt: return True
    if dst == ExpType.TyBool and src == ExpType.TyBool: return True
    if dst == ExpType.TyString and src == ExpType.TyString: return True
    return False

class SemanticAnalyzer:
    """
    - Construye/usa la TS global (ya lo haces).
    - Recorre el AST y:
      a) inserta declaraciones/uso en TS,
      b) infiere tipos de expresiones,
      c) valida condiciones (if/while/until),
      d) valida asignaciones y operadores,
      e) reporta errores con (línea, columna) estandarizados.
    """
    def __init__(self):
        self.ts = ScopedSymTab()
        self.errors: List[dict] = []  # [{msg, linea, columna}]
        self._reported_errors = set()  # evita duplicados exactos
    
    def _is_truthy_type(self, t: str) -> bool:
        """Tipos válidos como condición: bool o numéricos (int/float)."""
        return t in (ExpType.TyBool, ExpType.TyInt, ExpType.TyFloat)

    # ---------- API principal ----------
    def analyze(self, ast_root):
        if ast_root is None:
            return "[Semántico] AST vacío", "", []

        self._reported_errors.clear()
        self.errors.clear()

        self._visit(ast_root)

        return "", self.ts.print_all_custom(), self.errors

    # ---------- Utilidades de posición y reporte ----------
    def _pos(self, node) -> Tuple[int, int]:
        """Obtiene (linea, columna) del nodo o del primer descendiente que tenga token."""
        if node is None:
            return (0, 0)
        lin = getattr(node, "token_linea", None)
        col = getattr(node, "token_columna", None)
        if lin is not None and col is not None and lin != "" and col != "":
            try:
                return (int(lin), int(col))
            except Exception:
                return (0, 0)
        # buscar en hijos
        for ch in getattr(node, "hijos", []):
            l, c = self._pos(ch)
            if l or c:
                return (l, c)
        return (0, 0)

    def _report(self, msg: str, node):
        linea, columna = self._pos(node)
        key = f"{msg}|{linea}|{columna}"
        if key in self._reported_errors:
            return
        self._reported_errors.add(key)
        self.errors.append({"msg": msg, "linea": linea, "columna": columna})

    def _es_ident(self, node) -> bool:
        return (
            getattr(node, "tipo", "") == "id" or
            getattr(node, "token_tipo", "") == "Identificador"
        )

    # ---------- Inferencia de tipos en expresiones ----------
    def _infer(self, node) -> str:
        """
        Devuelve un ExpType.* e inmediatamente reporta errores de uso indebido
        de operadores (con línea/columna) cuando corresponda.
        """
        if node is None:
            return ExpType.TyError

        t = getattr(node, "tipo", "")
        v = getattr(node, "valor", "")

        # Literales
        if t == "numero":
            # tu léxico ya distingue enteros/reales; si quieres usar token_tipo, ajusta aquí
            lex = str(v)
            return ExpType.TyFloat if any(c in lex for c in ".eE") else ExpType.TyInt
        if t == "cadena":
            return ExpType.TyString
        if t == "booleano":
            return ExpType.TyBool

        # Identificadores
        if self._es_ident(node):
            name = node.valor
            if not self.ts.st_exists(name):
                self._report(f"Variable no declarada '{name}'", node)
                return ExpType.TyError
            return self.ts.st_lookup_type(name)

        # Unario "!"
        if t == "!":
            rt = self._infer(node.hijos[0] if node.hijos else None)
            if rt != ExpType.TyBool:
                self._report("Operador '!' requiere operando bool", node)
                return ExpType.TyError
            return ExpType.TyBool

        # Binarios / n-arios: valor del nodo es el operador
        if v in {"+", "-", "*", "/", "%", "^"}:
            lt = self._infer(node.hijos[0] if len(node.hijos) > 0 else None)
            rt = self._infer(node.hijos[1] if len(node.hijos) > 1 else None)

            if v == "%":
                if not (_is_integer(lt) and _is_integer(rt)):
                    self._report("Operador '%' requiere operandos enteros", node)
                    return ExpType.TyError
                return ExpType.TyInt

            # +,-,*,/,^ → numéricos
            if not (_is_numeric(lt) and _is_numeric(rt)):
                self._report(f"Operador '{v}' requiere operandos numéricos", node)
                return ExpType.TyError

            # potencia: resultado numérico con promoción
            if v == "^":
                return _promote(lt, rt)
            # los demás se promueven usual
            return _promote(lt, rt)

        # Relacionales
        if v in {"<", "<=", ">", ">=", "==", "!="}:
            lt = self._infer(node.hijos[0] if len(node.hijos) > 0 else None)
            rt = self._infer(node.hijos[1] if len(node.hijos) > 1 else None)
            # Regla: ambos numéricos, o del mismo tipo escalar (bool/bool, string/string)
            ok = False
            if _is_numeric(lt) and _is_numeric(rt):
                ok = True
            elif lt == rt and lt in (ExpType.TyBool, ExpType.TyString):
                ok = True
            if not ok:
                self._report("Operandos incompatibles en operador relacional", node)
                return ExpType.TyError
            return ExpType.TyBool

        # Lógicos (si decides soportarlos en el AST)
        if v in {"&&", "and", "||", "or"}:
            lt = self._infer(node.hijos[0] if len(node.hijos) > 0 else None)
            rt = self._infer(node.hijos[1] if len(node.hijos) > 1 else None)
            if lt != ExpType.TyBool or rt != ExpType.TyBool:
                self._report(f"Operador lógico '{v}' requiere operandos bool", node)
                return ExpType.TyError
            return ExpType.TyBool

        # Si el nodo es un contenedor (e.g., 'then', 'body'), intenta tipo del único hijo
        if getattr(node, "hijos", None):
            if len(node.hijos) == 1:
                return self._infer(node.hijos[0])
            # en otros contenedores sin operador, no hay tipo
        return ExpType.TyError

    # ---------- Recorrido principal ----------
    def _visit(self, node, parent=None):
        if node is None:
            return

        # (1) Declaraciones: nodo 'int'|'float'|'bool' con hijos id
        if node.tipo in TIPO_NODOS_DECL:
            vtype = TIPO_NODOS_DECL[node.tipo]
            for child in getattr(node, "hijos", []):
                if self._es_ident(child):
                    name = child.valor
                    linea = int(child.token_linea or 0)
                    # redeclaración en el scope actual
                    if self.ts.scopes[-1].exists(name):
                        self._report(f"Identificador redeclarado: {name}", child)
                    # inserta con valor inicial
                    self.ts.st_insert(name, linea, vtype)
            return  # no registrar estos ids como uso

        # (2) Asignación "=": LHS debe existir + compatibilidad de tipos con RHS
        if node.tipo == '=' and len(node.hijos) >= 2:
            lhs = node.hijos[0]
            rhs = node.hijos[1]

            if self._es_ident(lhs):
                name = lhs.valor
                if not self.ts.st_exists(name):
                    self._report(f"Variable no declarada '{name}'", lhs)
                else:
                    dst_t = self.ts.st_lookup_type(name)
                    src_t = self._infer(rhs)
                    if not _assignable(dst_t, src_t):
                        self._report(
                            f"Tipos incompatibles en asignación: {dst_t} = {src_t}",
                            node
                        )
                    else:
                        # Literal → actualiza valor; expresión → solo uso
                        lit = self._eval_literal(rhs)
                        if lit is not None:
                            self.ts.st_set_value(name, lit, lineno=int(lhs.token_linea or 0))
                        else:
                            self.ts.st_insert_use(name, int(lhs.token_linea or 0))

            # Visitar RHS para registrar usos internos
            self._visit(rhs, node)
            return

        # (3) cin: tipos soportados + existencia
        if node.tipo == 'cin' and node.hijos:
            for child in node.hijos:
                if self._es_ident(child):
                    name = child.valor
                    if not self.ts.st_exists(name):
                        self._report(f"Variable no declarada '{name}'", child)
                    else:
                        t = self.ts.st_lookup_type(name)
                        if t not in (ExpType.TyInt, ExpType.TyFloat, ExpType.TyBool, ExpType.TyString):
                            self._report(f"Tipo no soportado en entrada: {t}", child)
                        else:
                            self.ts.st_set_value(name, "input", lineno=int(child.token_linea or 0))
            return

        # (4) Control de flujo: condiciones deben ser bool
        if node.tipo == 'if':
            # hijos esperados: [cond, then, (else?)]
            if node.hijos:
                cond_t = self._infer(node.hijos[0])
                if not self._is_truthy_type(cond_t):
                    self._report(f"La condición de 'if' debe ser bool o numérica, recibió {cond_t}", node.hijos[0])
            # recorrer ramas
            for ch in node.hijos[1:]:
                self._visit(ch, node)
            return

        if node.tipo == 'while':
            if node.hijos:
                cond_t = self._infer(node.hijos[0])
                if not self._is_truthy_type(cond_t):
                    self._report(f"La condición del while debe ser bool o numérica, recibió {cond_t}", node.hijos[0])

                # cuerpo
                if len(node.hijos) > 1 and getattr(node.hijos[1], "tipo", "") == "body":
                    for stmt in node.hijos[1].hijos:
                        self._visit(stmt, node)
            return

        if node.tipo == 'do':
            # visitar cuerpo
            for ch in node.hijos:
                if getattr(ch, "tipo", "") == "body":
                    for stmt in ch.hijos:
                        self._visit(stmt, node)
                elif ch.tipo in ('until', 'while'):
                    if ch.hijos:
                        cond_t = self._infer(ch.hijos[0])
                        if not self._is_truthy_type(cond_t):
                            kw = ch.tipo
                            self._report(f"La condición del {kw} debe ser bool o numérica, recibió {cond_t}", ch.hijos[0])
                    

            return

        # (5) cout: solo visitar expresiones
        if node.tipo == 'cout':
            for ch in node.hijos:
                self._infer(ch)  # fuerza validación de tipos en expresiones
            return

        # (6) Uso de id fuera de LHS y fuera de '=' ya controlado
        if self._es_ident(node):
            name = node.valor
            if not self.ts.st_exists(name):
                self._report(f"Variable no declarada '{name}'", node)
            else:
                self.ts.st_insert_use(name, int(node.token_linea or 0))
            return

        # (7) Recorre hijos (y, de paso, valida expresiones sueltas)
        for ch in getattr(node, "hijos", []):
            # Si es operador/expresión, inferir para validar
            if getattr(node, "valor", "") in {"+","-","*","/","%","^","<","<=",">",">=","==","!=", "&&","and","||","or","!"}:
                self._infer(node)
                break
            self._visit(ch, node)

    # ---------- Literales ----------
    def _eval_literal(self, node) -> Optional[object]:
        if node is None:
            return None
        if node.tipo == "numero":
            try:
                lex = str(node.valor)
                return float(lex) if any(c in lex for c in ".eE") else int(lex)
            except Exception:
                return None
        if node.tipo == "cadena":
            val = str(node.valor)
            if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
                return val[1:-1]
            return val
        if node.tipo == "booleano":
            return True if str(node.valor).lower() == "true" else False
        if getattr(node, "hijos", None) and len(node.hijos) == 1:
            return self._eval_literal(node.hijos[0])
        return None
