# -*- coding: utf-8 -*-
# analizadores/symtab.py

from dataclasses import dataclass, field
from typing import Optional, List

# Tipos del lenguaje
class ExpType:
    TyInt = "int"
    TyFloat = "float"
    TyBool = "bool"
    TyString = "string"
    TyVoid = "void"
    TyError = "error"

@dataclass
class Bucket:
    name: str
    memloc: int
    type: str
    lines: List[int] = field(default_factory=list)
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

    # Inserta: si es primera vez, fija loc y type; sino, solo agrega línea
    def insert(self, name: str, lineno: int, loc: int, vtype: str) -> None:
        h = self._hash(name)
        b = self._table[h]
        while b is not None and b.name != name:
            b = b.next
        if b is None:
            newb = Bucket(name=name, memloc=loc, type=vtype, lines=[lineno], next=self._table[h])
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

    def print_table(self) -> str:
        out = []
        out.append("Variable Name      Type      Location   Line Numbers")
        out.append("-----------------  --------  --------   ------------")
        for i in range(self.SIZE):
            b = self._table[i]
            while b is not None:
                lines_str = " ".join(str(n) for n in b.lines)
                out.append(f"{b.name:<17}  {b.type:<8}  {b.memloc:<8}   {lines_str}")
                b = b.next
        return "\n".join(out)

# Versión con scopes sencillos (opcional para futuro)
class ScopedSymTab:
    def __init__(self):
        self.scopes: List[HashTable] = [HashTable()]
        self._next_loc = 0

    def _alloc_loc(self) -> int:
        loc = self._next_loc
        self._next_loc += 1
        return loc

    def push_scope(self): self.scopes.append(HashTable())
    def pop_scope(self):
        if len(self.scopes) > 1: self.scopes.pop()

    def _find_any(self, name: str) -> Optional[Bucket]:
        for tab in reversed(self.scopes):
            b = tab._find(name)
            if b is not None: return b
        return None

    def st_exists(self, name: str) -> bool: return self._find_any(name) is not None
    def st_lookup_type(self, name: str) -> str:
        b = self._find_any(name)
        return b.type if b else ExpType.TyError

    def st_insert(self, name: str, lineno: int, vtype: str, loc: int | None = None):
        cur = self.scopes[-1]
        if not cur.exists(name):
            cur.insert(name, lineno, self._alloc_loc() if loc is None else loc, vtype)
        else:
            # redeclaración en mismo scope: solo agrega línea; error lo reporta el analizador
            cur.insert(name, lineno, 0, vtype)

    def st_insert_use(self, name: str, lineno: int):
        b = self._find_any(name)
        if b is None: return
        # localizar la tabla que contiene a b e insertar uso
        for tab in reversed(self.scopes):
            if tab._find(name) is b:
                tab.insert(name, lineno, 0, b.type)
                break

    def print_all(self) -> str:
        out = []
        for i, tab in enumerate(self.scopes):
            out.append(f"--- Scope {i} ---")
            out.append(tab.print_table())
        return "\n".join(out)
