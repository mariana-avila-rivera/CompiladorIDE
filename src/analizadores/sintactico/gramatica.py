# -*- coding: utf-8 -*-
"""
Definición de gramática
Contiene las reglas de la gramática y métodos para obtener terminales y no terminales
"""


class GramaticaDefinicion:
    def __init__(self):
        self.gramatica = self._definir_gramatica()
        
    def _definir_gramatica(self):
        """Define las reglas de la gramática"""
        return {
            'programa': [['main', '{', 'lista_declaracion', '}', ';']],
            'lista_declaracion': [
                ['declaracion', 'lista_declaracion'],
                ['ε']
            ],
            'declaracion': [
                ['declaracion_variable'],
                ['sentencia']
            ],
            'declaracion_variable': [['tipo', 'lista_identificadores', ';']],
            'lista_identificadores': [['id', 'lista_identificadores_aux']],
            'lista_identificadores_aux': [
                [',', 'id', 'lista_identificadores_aux'],
                ['ε']
            ],
            'tipo': [['int'], ['float'], ['bool']],
            'sentencia': [
                ['seleccion'], ['iteracion'], ['repeticion'], 
                ['sent_in'], ['sent_out'], ['asignacion']
            ],
            'asignacion': [['id', 'asignacion_op']],
            'asignacion_op': [
                ['=', 'expresion', ';'],
                ['++', ';'],
                ['--', ';']
            ],
            'seleccion': [['if', '(', 'expresion', ')', 'then', 'lista_sentencias', 'seleccion_aux']],
            'seleccion_aux': [
                ['else', 'lista_sentencias', 'end',';'],
                ['end', ';']
            ],
            'iteracion': [['while', '(', 'expresion', ')', 'lista_sentencias', 'end', ';']],
            'repeticion': [
                ['do', 'lista_sentencias', 'until', '(', 'expresion', ')', ';'],
                ['do', 'lista_sentencias', 'while', '(', 'expresion', ')', 'lista_sentencias', 'end', ';']
            ],
            'sent_in': [['cin', '>>', 'id', ';']],
            'sent_out': [['cout', '<<', 'lista_salida', ';']],
            'lista_salida': [['elemento_salida', 'lista_salida_aux']],
            'lista_salida_aux': [
                ['<<', 'elemento_salida', 'lista_salida_aux'],
                ['ε']
            ],
            'elemento_salida': [['cadena'], ['expresion']],
            'lista_sentencias': [
                ['sentencia', 'lista_sentencias'],
                ['ε']
            ],
            # CAMBIOS AQUÍ: Nueva jerarquía de expresiones con operadores lógicos
            'expresion': [['expresion_logica', 'expresion_aux']],
            'expresion_aux': [['ε']],
            
            # Nuevas reglas para expresiones lógicas
            'expresion_logica': [['expresion_and', 'expresion_logica_aux']],
            'expresion_logica_aux': [
                ['||', 'expresion_and', 'expresion_logica_aux'],
                ['ε']
            ],
            
            'expresion_and': [['expresion_relacional', 'expresion_and_aux']],
            'expresion_and_aux': [
                ['&&', 'expresion_relacional', 'expresion_and_aux'],
                ['ε']
            ],
            
            'expresion_relacional': [['expresion_simple', 'expresion_relacional_aux']],
            'expresion_relacional_aux': [
                ['rel_op', 'expresion_simple'],
                ['ε']
            ],
            
            'rel_op': [['<'], ['<='], ['>'], ['>='], ['=='], ['!=']],
            'expresion_simple': [['termino', 'expresion_simple_aux']],
            'expresion_simple_aux': [
                ['suma_op', 'termino', 'expresion_simple_aux'],
                ['ε']
            ],
            'suma_op': [['+'], ['-']],
            'termino': [['componente', 'termino_aux']],
            'termino_aux': [
                ['operador_termino', 'componente', 'termino_aux'],
                ['ε']
            ],
            'operador_termino': [['mult_op'], ['^']],
            'mult_op': [['*'], ['/'], ['%']],
            'componente': [
                ['(', 'expresion', ')'],
                ['numero'],
                ['id'],
                ['booleano'],
                ['!', 'componente']
            ],
            'booleano': [['true'], ['false']],
            'cadena': [['"cualquier_texto"']]
        }
    
    def obtener_terminales(self):
        """Obtiene todos los símbolos terminales de la gramática"""
        terminales = set()
        for producciones in self.gramatica.values():
            for produccion in producciones:
                for simbolo in produccion:
                    if simbolo not in self.gramatica and simbolo != 'ε':
                        terminales.add(simbolo)
        terminales.add('$')  # Símbolo de fin de cadena
        return terminales
    
    def obtener_no_terminales(self):
        """Obtiene todos los no terminales de la gramática"""
        return set(self.gramatica.keys())
        
    def obtener_gramatica(self):
        """Retorna la gramática completa"""
        return self.gramatica
