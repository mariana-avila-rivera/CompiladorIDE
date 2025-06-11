# -*- coding: utf-8 -*-
"""
Constructor de tabla LL(1)
Contiene la lógica para construir la tabla de análisis LL(1)
"""


class ConstructorTablaLL1:
    def __init__(self, gramatica, no_terminales, terminales):
        self.gramatica = gramatica
        self.no_terminales = no_terminales
        self.terminales = terminales
        
    def construir_tabla(self, primeros, siguientes):
        """Construye la tabla de análisis LL(1)"""
        tabla_ll1 = {}
        
        # Inicializar tabla
        for no_terminal in self.no_terminales:
            tabla_ll1[no_terminal] = {}
            for terminal in self.terminales:
                tabla_ll1[no_terminal][terminal] = None
        
        # Llenar la tabla
        for no_terminal in self.no_terminales:
            for i, produccion in enumerate(self.gramatica[no_terminal]):
                # Para cada terminal en PRIMEROS(producción)
                primeros_prod = self._calcular_primeros_cadena(produccion, primeros)
                
                for terminal in primeros_prod - {'ε'}:
                    if tabla_ll1[no_terminal][terminal] is None:
                        tabla_ll1[no_terminal][terminal] = (no_terminal, produccion)
                    else:
                        # Conflicto en la tabla
                        print(f"Conflicto en M[{no_terminal}, {terminal}]")
                
                # Si ε ∈ PRIMEROS(producción)
                if 'ε' in primeros_prod:
                    for terminal in siguientes[no_terminal]:
                        if tabla_ll1[no_terminal][terminal] is None:
                            tabla_ll1[no_terminal][terminal] = (no_terminal, produccion)
                        else:
                            print(f"Conflicto en M[{no_terminal}, {terminal}]")
        
        return tabla_ll1
    
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
