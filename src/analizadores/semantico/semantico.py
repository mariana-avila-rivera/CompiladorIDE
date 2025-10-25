# -*- coding: utf-8 -*-
# analizadores/semantico.py

from typing import List
from .symtab import ScopedSymTab, ExpType

TIPO_NODOS_DECL = {"int": ExpType.TyInt, "float": ExpType.TyFloat, "bool": ExpType.TyBool}

class SemanticAnalyzer:
    def __init__(self):
        self.ts = ScopedSymTab()
        self.errors: List[str] = []

    def analyze(self, ast_root):
        """
        Recorre el AST:
        - Inserta declaraciones: nodos cuyo tipo sea 'int'|'float'|'bool' con hijos identificadores.
        - Registra usos de identificadores en expresiones y sentencias.
        - Imprime Hash Table al final.
        """
        if ast_root is None:
            print("[Semántico] AST vacío")
            return

        # Con tu gramática actual, basta un solo scope (main). 
        # Si después hay bloques con variables locales, activa push/pop_scope en los nodos de bloque.
        self._visit(ast_root)

        # Imprimir TS a terminal
        print("\n===== HASH TABLE =====")
        print(self.ts.print_all())
        print("======================\n")

        if self.errors:
            print("ERRORES SEMÁNTICOS:")
            for e in self.errors:
                print(" -", e)

    # ----------------- Recorrido -----------------

    def _visit(self, node, parent=None):
        if node is None: return

        # 1) Declaraciones: nodo tipo 'int'|'float'|'bool' con hijos identificadores
        if node.tipo in TIPO_NODOS_DECL:
            vtype = TIPO_NODOS_DECL[node.tipo]
            for child in getattr(node, "hijos", []):
                if getattr(child, "tipo", "") == "id":
                    name = child.valor
                    linea = int(child.token_linea or 0)
                    # redeclaración en mismo scope
                    if self.ts.scopes[-1].exists(name):
                        self.errors.append(f"[L{linea}] Redeclaración de '{name}'")
                    self.ts.st_insert(name, linea, vtype)
            # seguir recorriendo por si contienen algo más
            for ch in node.hijos:
                self._visit(ch, node)
            return

        # 2) Uso de identificadores (no en lado de tipo de declaración)
        if node.tipo == "id":
            name = node.valor
            linea = int(node.token_linea or 0)
            if not self.ts.st_exists(name):
                self.errors.append(f"[L{linea}] Variable no declarada '{name}'")
            else:
                self.ts.st_insert_use(name, linea)
            # id es hoja; return
            return

        # 3) Posibles puntos de scope (si los quisieras activar)
        # if node.tipo in ("then", "else", "while", "do"):
        #     self.ts.push_scope()
        #     for ch in node.hijos: self._visit(ch, node)
        #     self.ts.pop_scope()
        #     return

        # Recorre hijos por defecto
        for ch in getattr(node, "hijos", []):
            self._visit(ch, node)
