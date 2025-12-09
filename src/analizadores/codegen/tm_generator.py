
class TMGenerator:
    def __init__(self):
        self.instructions = []
        self.location = 0
        self.temp_offset = 0  # Offset para variables temporales en dmem

    def generate(self, pcode_instructions, output_path):
        self.instructions = []
        self.location = 0
        self.temp_offset = 1000 # Empezar variables temporales en 1000 para no chocar con globales
        
        # Preludio estándar
        self._emit_comment("Standard prelude:")
        self._emit("LDC", 6, 1, 0, "load gp with 1 (start of globals)")
        self._emit("LDA", 5, 0, 6, "copy gp to fp")
        self._emit("ST", 0, 0, 0, "clear location 0")
        
        # Traducir P-Code a TM
        # Mapeo de etiquetas P-Code a líneas TM
        label_map = {}
        # Primera pasada para encontrar etiquetas (o usar backpatching, aquí simple)
        # Como P-Code es lineal, podemos ir generando.
        # Pero los saltos (FJP L1) necesitan saber la línea de L1.
        # Así que mejor procesamos P-Code en memoria primero.
        
        # Simulación de pila para traducción
        # P-Code es stack-based, TM es register-based (pero usaremos memoria como pila para simplicidad inicial)
        # SP (Stack Pointer) será simulado o usaremos un registro (ej. R6 es GP, R5 es FP).
        # Usaremos dmem como pila. R0 (AC) acumulador.
        
        # Estrategia simple:
        # Cada instrucción P-Code manipula una pila conceptual.
        # En TM, usaremos dmem[sp] como la pila.
        # sp estará en un registro, digamos R4 (no estándar pero útil).
        # O mejor, seguimos el estilo de euclid.tm: usar memoria relativa a FP/GP.
        
        # Para simplificar la traducción P-Code -> TM sin un análisis complejo de registros:
        # Implementaremos una "Máquina de Pila sobre TM".
        # R5 = FP (Frame Pointer)
        # R6 = GP (Global Pointer)
        # R4 = SP (Stack Pointer) - Apunta al tope de la pila en dmem
        
        self._emit("LDC", 4, 100, 0, "init SP at 100") # Pila empieza en 100
        
        # Mapa de etiquetas P-Code -> Instrucción TM
        pcode_labels = {}
        # Mapa de saltos pendientes: {tm_line: pcode_label}
        pending_jumps = {}
        
        for instr in pcode_instructions:
            parts = instr.replace(';', '').split()
            op = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            
            # Es una etiqueta? (L1:)
            if op.endswith(':'):
                label = op[:-1]
                pcode_labels[label] = self.location
                continue
                
            self._emit_comment(f"-> {instr}")
            
            if op == 'ldc': # Load Constant
                # Manejar flotantes
                try:
                    val = float(arg)
                except ValueError:
                    val = 0.0 # Fallback
                self._emit("LDC", 0, val, 0, "load const")
                self._push_ac()
                
            elif op == 'lda': # Load Address (Global var por nombre)
                # Necesitamos un mapa de variables -> direcciones
                # Por ahora, usaremos un hash simple del nombre para offset (muy hacky pero funcional para demo)
                # O mejor, asignamos offsets secuenciales.
                offset = self._get_var_offset(arg)
                self._emit("LDC", 0, offset, 0, "load address") # Cargar offset
                # Sumar GP si fuera necesario, pero asumimos dmem[offset] directo para globales
                self._push_ac()
                
            elif op == 'lod': # Load Value (Indirect)
                # Arg es el nombre de la variable
                offset = self._get_var_offset(arg)
                self._emit("LD", 0, offset, 6, "load val from global") # 6=GP
                self._push_ac()
                
            elif op == 'sto': # Store (tope: val, tope-1: addr)
                self._pop_to(1) # Val en R1
                self._pop_to(2) # Addr en R2 (offset)
                # TM ST toma: ST r, d(s) -> mem[d+s] = r
                # Queremos mem[R2 + GP] = R1.
                # Pero ST usa constante para d. No podemos usar registro para d.
                # Truco: ST R1, 0(R2) si R2 tiene la dirección absoluta.
                # Como R2 tiene offset, necesitamos dirección absoluta.
                # Asumimos que GP=0 para simplificar, entonces R2 es dir abs.
                # Pero espera, 'lda' arriba cargó el offset.
                # Si usamos GP (R6), ST R1, offset(R6). Pero offset está en R2!
                # TM no tiene direccionamiento indirecto registro+registro para ST fácilmente sin sumar.
                # Solución: Calcular dirección absoluta en R2.
                self._emit_ro("ADD", 2, 2, 6, "calc abs addr (offset+GP)")
                self._emit("ST", 1, 0, 2, "store val at addr")
                
            elif op == 'adi': # Add
                self._binary_op("ADD")
            elif op == 'sbi': # Sub
                self._binary_op("SUB")
            elif op == 'mpi': # Mul
                self._binary_op("MUL")
            elif op == 'dvi': # Div
                self._binary_op("DIV")
            elif op == 'pwr': # Power
                self._binary_op("PWR")
            
            elif op == 'equ': self._cmp_op("JEQ")
            elif op == 'neq': self._cmp_op("JNE")
            elif op == 'les': self._cmp_op("JLT")
            elif op == 'leq': self._cmp_op("JLE")
            elif op == 'grt': self._cmp_op("JGT")
            elif op == 'geq': self._cmp_op("JGE")
                
            elif op == 'wrt': # Write
                self._pop_to(0)
                comment = f"write:{arg}" if arg else "write"
                self._emit_ro("OUT", 0, 0, 0, comment)
                
            elif op == 'rdi': # Read Integer (to address at top)
                comment = f"read:{arg}" if arg else "read to ac"
                self._emit_ro("IN", 0, 0, 0, comment)
                self._pop_to(2) # Addr en R2
                self._emit_ro("ADD", 2, 2, 6, "calc abs addr")
                self._emit("ST", 0, 0, 2, "store read val")
                
            elif op == 'fjp': # False Jump
                self._pop_to(0)
                # JEQ r, d(s) -> if r==0 PC=d+s
                # Saltamos si es falso (0)
                pending_jumps[self.location] = arg
                self._emit("JEQ", 0, 0, 0, "jump if false (patch later)")
                
            elif op == 'ujp': # Unconditional Jump
                pending_jumps[self.location] = arg
                self._emit("LDC", 7, 0, 0, "jump (patch later)")
                
            elif op == 'stp': # Stop
                self._emit_ro("HALT", 0, 0, 0, "stop")

        # Backpatching de saltos
        for loc, label in pending_jumps.items():
            target = pcode_labels.get(label)
            if target is not None:
                # Calcular salto relativo o absoluto
                # LDA 7, abs(0) es salto absoluto a abs.
                # JEQ 0, abs(0) es salto absoluto a abs.
                # Reemplazar instrucción
                
                # Encontrar el índice en self.instructions que corresponde a 'loc'
                # Como self.instructions incluye comentarios, el índice no es 'loc'.
                # 'loc' es el número de instrucción TM.
                # Necesitamos buscar la línea que empieza con "loc:"
                
                target_idx = -1
                for i, line in enumerate(self.instructions):
                    if line.strip().startswith(f"{loc}:"):
                        target_idx = i
                        break
                
                if target_idx != -1:
                    instr = self.instructions[target_idx]
                    # Formato: "  9:    JEQ  0,       0(0) jump..."
                    parts = instr.split()
                    # parts[0] es "9:", parts[1] es "JEQ"
                    opcode = parts[1] 
                    
                    # Reconstruir instrucción con target
                    if opcode == 'LDC':
                        # Salto incondicional: LDC 7, target(0) -> PC = target
                        self.instructions[target_idx] = f"{loc:3}:    {opcode:4}  7,{target:8}(0) jump to {label}"
                    else:
                        # Salto condicional: JEQ 0, target(0) -> if AC==0 PC=target
                        self.instructions[target_idx] = f"{loc:3}:    {opcode:4}  0,{target:8}(0) jump to {label}"

        # Escribir archivo
        with open(output_path, 'w') as f:
            for line in self.instructions:
                f.write(line + '\n')
        
        return self.instructions
                
    def _emit(self, op, r, d, s, comment=""):
        self.instructions.append(f"{self.location:3}:    {op:4} {r:1},{d:8}({s}) {comment}")
        self.location += 1

    def _emit_ro(self, op, r, s, t, comment=""):
        self.instructions.append(f"{self.location:3}:    {op:4} {r:1},{s:1},{t:1} {comment}")
        self.location += 1
        
    def _emit_comment(self, comment):
        self.instructions.append(f"* {comment}")

    def _push_ac(self):
        # ST R0, 0(R4) ; mem[sp] = ac
        self._emit("ST", 0, 0, 4, "push ac")
        # LDA R4, 1(R4) ; sp++
        self._emit("LDA", 4, 1, 4, "sp++")
        
    def _pop_to(self, reg):
        # LDA R4, -1(R4) ; sp--
        self._emit("LDA", 4, -1, 4, "sp--")
        # LD Reg, 0(R4) ; reg = mem[sp]
        self._emit("LD", reg, 0, 4, f"pop to R{reg}")

    def _cmp_op(self, jump_op):
        self._pop_to(1) # Right
        self._pop_to(0) # Left
        self._emit_ro("SUB", 0, 0, 1, "cmp: left - right")
        self._emit(jump_op, 0, 2, 7, "jump if true")
        self._emit("LDC", 0, 0, 0, "false")
        self._emit("LDA", 7, 1, 7, "jump to end")
        self._emit("LDC", 0, 1, 0, "true")
        self._push_ac()
        
    def _binary_op(self, tm_op):
        self._pop_to(1) # Right operand
        self._pop_to(0) # Left operand
        self._emit_ro(tm_op, 0, 0, 1, f"op {tm_op}") # R0 = R0 op R1
        self._push_ac() # Push result

    def _get_var_offset(self, var_name):
        # Simple hash map para demo. En real usar tabla de símbolos.
        if not hasattr(self, 'var_map'):
            self.var_map = {}
            self.next_var = 0
        
        if var_name not in self.var_map:
            self.var_map[var_name] = self.next_var
            self.next_var += 1
            
        return self.var_map[var_name]
