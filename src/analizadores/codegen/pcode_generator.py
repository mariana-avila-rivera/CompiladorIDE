
class PCodeGenerator:
    def __init__(self):
        self.instructions = []
        self.label_count = 0

    def generate(self, ast):
        self.instructions = []
        self.label_count = 0
        if ast:
            self._process_node(ast)
        return self.instructions

    def _emit(self, instr):
        self.instructions.append(f"{instr};")

    def _new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def _emit_label(self, label):
        self.instructions.append(f"{label}:")

    def _process_node(self, node):
        if not node:
            return

        tipo = node.tipo
        hijos = node.hijos
        valor = node.valor

        # Programa
        if tipo == 'programa':
            for hijo in hijos:
                self._process_node(hijo)
            self._emit('stp')

        # Bloque de sentencias y contenedores
        elif tipo in ('body', 'then', 'else', 'bloque', 'lista_declaracion', 'declaracion', 'sentencia', 'lista_sentencias'):
            for hijo in hijos:
                self._process_node(hijo)

        # Declaraciones (ignoradas en P-Code simple o solo espacio)
        elif tipo in ('int', 'float', 'bool', 'string', 'void'):
            # Si hay inicialización, procesarla
            pass

        # Asignación (=)
        elif tipo == '=':
            # Hijos: [id, expresion]
            if len(hijos) >= 2:
                id_node = hijos[0]
                expr_node = hijos[1]
                
                # lda id (Cargar dirección de variable)
                self._emit(f"lda {id_node.valor}")
                # codigo expresion
                self._process_node(expr_node)
                # sto (Almacenar valor en dirección)
                self._emit("sto")

        # If
        elif tipo == 'if':
            # Hijos: [cond, then, (else)?]
            if len(hijos) >= 2:
                cond = hijos[0]
                then_block = hijos[1]
                else_block = hijos[2] if len(hijos) > 2 else None

                l_else = self._new_label()
                l_end = self._new_label()

                self._process_node(cond)
                self._emit(f"fjp {l_else}")
                
                self._process_node(then_block)
                self._emit(f"ujp {l_end}")
                
                self._emit_label(l_else)
                if else_block:
                    self._process_node(else_block)
                
                self._emit_label(l_end)

        # While
        elif tipo == 'while':
            # Hijos: [cond, body]
            if len(hijos) >= 2:
                cond = hijos[0]
                body = hijos[1]

                l_start = self._new_label()
                l_end = self._new_label()

                self._emit_label(l_start)
                self._process_node(cond)
                self._emit(f"fjp {l_end}")
                
                self._process_node(body)
                self._emit(f"ujp {l_start}")
                
                self._emit_label(l_end)

        # Do (Until / While)
        elif tipo == 'do':
            # Hijos: [body, cond_wrapper]
            if len(hijos) >= 2:
                body = hijos[0]
                cond_wrapper = hijos[1] # until o while
                
                l_start = self._new_label()
                self._emit_label(l_start)
                
                self._process_node(body)
                
                if cond_wrapper.hijos:
                    cond = cond_wrapper.hijos[0]
                    self._process_node(cond)
                    
                    if cond_wrapper.tipo == 'until':
                        # Repetir hasta que sea verdadero -> Repetir mientras sea falso
                        self._emit(f"fjp {l_start}")
                    elif cond_wrapper.tipo == 'while':
                        # Repetir mientras sea verdadero
                        # Si es verdadero, saltar al inicio.
                        l_exit = self._new_label()
                        self._emit(f"fjp {l_exit}")
                        self._emit(f"ujp {l_start}")
                        self._emit_label(l_exit)

        # Input (cin)
        elif tipo == 'cin':
            for hijo in hijos:
                # lda id
                self._emit(f"lda {hijo.valor}")
                self._emit(f"rdi {hijo.valor}")

        # Output (cout)
        elif tipo == 'cout':
            for hijo in hijos:
                self._process_node(hijo)
                if hijo.tipo == 'id':
                    self._emit(f"wrt {hijo.valor}")
                else:
                    self._emit("wrt")

        # Operaciones Binarias
        elif tipo in ('+', '-', '*', '/', '%', '^', '==', '!=', '<', '<=', '>', '>=', '&&', '||', 'and', 'or'):
            if len(hijos) >= 2:
                self._process_node(hijos[0])
                self._process_node(hijos[1])
                
                op_map = {
                    '+': 'adi', '-': 'sbi', '*': 'mpi', '/': 'dvi', '%': 'mod', '^': 'pwr',
                    '==': 'equ', '!=': 'neq', '<': 'les', '<=': 'leq', '>': 'grt', '>=': 'geq',
                    '&&': 'and', 'and': 'and', '||': 'or', 'or': 'or'
                }
                self._emit(op_map.get(tipo, 'nop'))

        # Identificador (R-Value)
        elif tipo == 'id':
            self._emit(f"lod {valor}")

        # Literales
        elif tipo in ('numero', 'entero', 'flotante'):
            self._emit(f"ldc {valor}")
        
        elif tipo == 'booleano':
            val = 1 if str(valor).lower() == 'true' else 0
            self._emit(f"ldc {val}")
            
        elif tipo == 'cadena':
            self._emit(f"ldc '{valor}'")
