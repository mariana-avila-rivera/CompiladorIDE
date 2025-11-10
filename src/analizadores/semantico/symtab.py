# -*- coding: utf-8 -*-
# analizadores/semantico/symtab.py

from dataclasses import dataclass, field
from typing import Optional, List, Dict

# Tipos del lenguaje
class ExpType:
    TyInt = "int"
    TyFloat = "float"
    TyBool = "bool"
    TyString = "string"
    TyVoid = "void"
    TyError = "error"

def _default_value_for(vtype: str):
    if vtype == ExpType.TyInt: return 0
    if vtype == ExpType.TyFloat: return 0.0
    if vtype == ExpType.TyBool: return False
    if vtype == ExpType.TyString: return ""
    return 0

@dataclass
class Bucket:
    name: str
    memloc: int                 # Registro
    type: str                   # Tipo de dato
    lines: List[int] = field(default_factory=list)  # Num. de línea (lista)
    last_value: object = 0      # Valor (último)
    scope: str = "Global" 
    next: Optional["Bucket"] = None

class HashTable:
    def __init__(self, size: int = 211):
        self.SIZE = size
        self._table: List[Optional[Bucket]] = [None] * self.SIZE

    def _hash(self, key: str) -> int:
        SHIFT = 4
        temp = 0
        for ch in key:
            temp = ((temp << SHIFT) + ord(ch)) % self.SIZE
        return temp

    def insert(self, name: str, lineno: int, loc: int, vtype: str, initial_value=None, scope: str = "Global") -> None:
        """
        Inserta símbolo. Si no existía: fija registro, tipo y valor inicial.
        Si ya existía: sólo agrega línea de uso.
        """
        h = self._hash(name)
        b = self._table[h]
        while b is not None and b.name != name:
            b = b.next
        if b is None:
            if initial_value is None:
                initial_value = _default_value_for(vtype)
            newb = Bucket(name=name, memloc=loc, type=vtype,
                          lines=[lineno], last_value=initial_value,
                          scope=scope, 
                          next=self._table[h])
            self._table[h] = newb
        else:
            b.lines.append(lineno)

    def _find(self, name: str) -> Optional[Bucket]:
        h = self._hash(name)
        b = self._table[h]
        while b is not None and b.name != name:
            b = b.next
        return b

    def lookup_loc(self, name: str) -> int:
        b = self._find(name)
        return b.memloc if b else -1

    def lookup_type(self, name: str) -> str:
        b = self._find(name)
        return b.type if b else ExpType.TyError

    def exists(self, name: str) -> bool:
        return self._find(name) is not None

    def set_value(self, name: str, value, lineno: Optional[int] = None):
        """Actualiza el último valor del símbolo y registra línea si se da."""
        b = self._find(name)
        if not b: return
        b.last_value = value
        if lineno is not None:
            b.lines.append(lineno)

  
class ScopedSymTab:
    def __init__(self):
        self.scopes: List[HashTable] = [HashTable()]
        self._all_scopes: List[HashTable] = [self.scopes[0]]  # <<< histórico p/ impresión
        self._next_loc = 0

    def _alloc_loc(self) -> int:
        loc = self._next_loc
        self._next_loc += 1
        return loc

    # Manejo de ámbitos
    def push_scope(self):
        new_tab = HashTable()
        self.scopes.append(new_tab)
        self._all_scopes.append(new_tab)  # <<< mantener referencia aunque se haga pop

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def _find_any(self, name: str) -> Optional[Bucket]:
        for tab in reversed(self.scopes):
            b = tab._find(name)
            if b is not None: return b
        return None

    # API
    def st_exists(self, name: str) -> bool: 
        return self._find_any(name) is not None

    def st_lookup_type(self, name: str) -> str:
        b = self._find_any(name)
        return b.type if b else ExpType.TyError

    def st_insert(self, name: str, lineno: int, vtype: str, initial_value=None):
        """Inserta en el scope actual con valor inicial por tipo si no se da."""
        cur = self.scopes[-1]
        scope_label = "Global" if len(self.scopes) == 1 else "Local"
        if not cur.exists(name):
            cur.insert(name, lineno, self._alloc_loc(), vtype, initial_value, scope=scope_label)
        else:
            # redeclaración en mismo scope: solo agrega línea; el error lo reporta quien llama
            cur.insert(name, lineno, 0, vtype, scope=scope_label)

    def st_insert_use(self, name: str, lineno: int):
        """Registra uso en el símbolo más interno que lo defina."""
        b = self._find_any(name)
        if b is None: return
        for tab in reversed(self.scopes):
            if tab._find(name) is b:
                tab.insert(name, lineno, 0, b.type, scope=b.scope)
                break

    def st_set_value(self, name: str, value, lineno: Optional[int] = None):
        b = self._find_any(name)
        if b is None: return
        for tab in reversed(self.scopes):
            if tab._find(name) is b:
                tab.set_value(name, value, lineno)
                break

    def print_all_custom(self) -> str:
        """Imprime TODOS los scopes (global + locales, incluidos los ya cerrados) con columna 'Ámbito'."""
        head = ["Identificador", "Registro", "Valor", "Tipo de dato", "Ámbito", "Num. de Linea"]
        def fmt_row(cols):
            return (
                f"{str(cols[0]):<18}  "
                f"{str(cols[1]):<9}  "
                f"{str(cols[2]):<12}  "
                f"{str(cols[3]):<12}  "
                f"{str(cols[4]):<8}  "
                f"{str(cols[5])}"
            )

        out = []
        out.append(fmt_row(head))
        out.append(fmt_row([
            "-"*len(head[0]),
            "-"*len(head[1]),
            "-"*len(head[2]),
            "-"*len(head[3]),
            "-"*len(head[4]),
            "-"*len(head[5]),
        ]))

        # Recolectar todos los buckets de todos los scopes (histórico)
        items: List[Bucket] = []
        for tab in self._all_scopes:  # <<< histórico
            for i in range(tab.SIZE):
                b = tab._table[i]
                while b is not None:
                    items.append(b)
                    b = b.next

        # Orden estable por memloc
        items.sort(key=lambda x: x.memloc)

        for b in items:
            unique_lines = sorted(b.lines)
            lines_str = ",".join(str(n) for n in unique_lines)
            if b.last_value == "input":
                val_str = "<input>"
            elif isinstance(b.last_value, bool):
                val_str = "true" if b.last_value else "false"
            elif b.last_value is None:
                val_str = "<undefined>"
            else:
                val_str = str(b.last_value)

            out.append(fmt_row([
                b.name, b.memloc, val_str, b.type, b.scope, lines_str if lines_str else "0"
            ]))
        return "\n".join(out)
