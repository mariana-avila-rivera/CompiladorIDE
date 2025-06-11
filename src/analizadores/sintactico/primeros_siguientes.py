# -*- coding: utf-8 -*-
"""
Calculador de conjuntos PRIMEROS y SIGUIENTES
Contiene la lógica para calcular los conjuntos PRIMEROS y SIGUIENTES de la gramática
"""


class CalculadorPrimerosSiguientes:
    def __init__(self, gramatica, terminales, no_terminales):
        self.gramatica = gramatica
        self.terminales = terminales
        self.no_terminales = no_terminales
        
    def calcular_primeros(self):
        """Calcula los conjuntos PRIMEROS para todos los símbolos"""
        primeros = {}
        
        # Inicializar conjuntos PRIMEROS
        for simbolo in self.no_terminales | self.terminales:
            primeros[simbolo] = set()
        
        # Inicializar PRIMEROS para epsilon
        primeros['ε'] = {'ε'}
        
        # PRIMEROS de terminales
        for terminal in self.terminales:
            primeros[terminal].add(terminal)
        
        # Repetir hasta que no haya cambios
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                size_anterior = len(primeros[no_terminal])
                
                for produccion in self.gramatica[no_terminal]:
                    if produccion == ['ε']:
                        primeros[no_terminal].add('ε')
                    else:
                        self._calcular_primeros_produccion(no_terminal, produccion, primeros)
                
                if len(primeros[no_terminal]) > size_anterior:
                    cambio = True
        
        return primeros
    
    def _calcular_primeros_produccion(self, no_terminal, produccion, primeros):
        """Calcula PRIMEROS para una producción específica"""
        i = 0
        while i < len(produccion):
            simbolo = produccion[i]
            
            # Agregar PRIMEROS(simbolo) - {ε} a PRIMEROS(no_terminal)
            primeros_simbolo = primeros[simbolo] - {'ε'}
            primeros[no_terminal].update(primeros_simbolo)
            
            # Si ε no está en PRIMEROS(simbolo), parar
            if 'ε' not in primeros[simbolo]:
                break
            
            i += 1
        
        # Si todos los símbolos pueden derivar ε, agregar ε
        if i == len(produccion):
            primeros[no_terminal].add('ε')
    
    def calcular_siguientes(self, primeros):
        """Calcula los conjuntos SIGUIENTES para todos los no terminales"""
        siguientes = {}
        
        # Inicializar conjuntos SIGUIENTES
        for no_terminal in self.no_terminales:
            siguientes[no_terminal] = set()
        
        # SIGUIENTES del símbolo inicial contiene $
        siguientes['programa'].add('$')
        
        # Repetir hasta que no haya cambios
        cambio = True
        while cambio:
            cambio = False
            
            for no_terminal in self.no_terminales:
                for produccion in self.gramatica[no_terminal]:
                    if produccion != ['ε']:
                        size_anterior = sum(len(siguientes[nt]) for nt in self.no_terminales)
                        self._calcular_siguientes_produccion(
                            no_terminal, produccion, siguientes, primeros
                        )
                        size_actual = sum(len(siguientes[nt]) for nt in self.no_terminales)
                        
                        if size_actual > size_anterior:
                            cambio = True
        
        return siguientes
    
    def _calcular_siguientes_produccion(self, no_terminal, produccion, siguientes, primeros):
        """Calcula SIGUIENTES para una producción específica"""
        for i, simbolo in enumerate(produccion):
            if simbolo in self.no_terminales:
                # Obtener PRIMEROS de la subcadena siguiente
                beta = produccion[i+1:]
                primeros_beta = self._calcular_primeros_cadena(beta, primeros)
                
                # Agregar PRIMEROS(β) - {ε} a SIGUIENTES(A)
                siguientes[simbolo].update(primeros_beta - {'ε'})
                
                # Si ε ∈ PRIMEROS(β), agregar SIGUIENTES(no_terminal) a SIGUIENTES(A)
                if 'ε' in primeros_beta or not beta:
                    siguientes[simbolo].update(siguientes[no_terminal])
    
    def _calcular_primeros_cadena(self, cadena, primeros):
        """Calcula PRIMEROS de una cadena de símbolos"""
        if not cadena:
            return {'ε'}
        
        resultado = set()
        
        for simbolo in cadena:
            # Verificar si el símbolo existe en primeros
            if simbolo not in primeros:
                if simbolo == 'ε':
                    primeros[simbolo] = {'ε'}
                else:
                    # Si es un terminal no reconocido, agregarlo
                    primeros[simbolo] = {simbolo}
            
            primeros_simbolo = primeros[simbolo] - {'ε'}
            resultado.update(primeros_simbolo)
            
            if 'ε' not in primeros[simbolo]:
                break
        else:
            resultado.add('ε')
        
        return resultado
