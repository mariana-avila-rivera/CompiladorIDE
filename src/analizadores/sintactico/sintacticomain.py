# -*- coding: utf-8 -*-
"""
Analizador sintáctico principal
Contiene la clase principal AnalizadorSintactico con la lógica de análisis LL(1)
"""

from .gramatica import GramaticaDefinicion
from .primeros_siguientes import CalculadorPrimerosSiguientes
from .tabla_ll1 import ConstructorTablaLL1
from .analizador_ll1 import AnalizadorLL1
from .arbol_sintactico import NodoArbol


class AnalizadorSintactico:
    def __init__(self):
        self.gramatica_def = GramaticaDefinicion()
        self.gramatica = self.gramatica_def.obtener_gramatica()
        self.terminales = self.gramatica_def.obtener_terminales()
        self.no_terminales = self.gramatica_def.obtener_no_terminales()
        
        self.calculador_ps = CalculadorPrimerosSiguientes(
            self.gramatica, self.terminales, self.no_terminales
        )
        self.constructor_tabla = ConstructorTablaLL1(
            self.gramatica, self.no_terminales, self.terminales
        )
        self.analizador_ll1 = AnalizadorLL1(self.terminales, self.no_terminales)
        
        self.primeros = {}
        self.siguientes = {}
        self.tabla_ll1 = {}
        self.arbol_sintactico = None
        self.errores = []
        
    def calcular_primeros(self):
        """Calcula los conjuntos PRIMEROS para todos los símbolos"""
        self.primeros = self.calculador_ps.calcular_primeros()
        
    def calcular_siguientes(self):
        """Calcula los conjuntos SIGUIENTES para todos los no terminales"""
        self.siguientes = self.calculador_ps.calcular_siguientes(self.primeros)
        
    def construir_tabla_ll1(self):
        """Construye la tabla de análisis LL(1)"""
        self.tabla_ll1 = self.constructor_tabla.construir_tabla(
            self.primeros, self.siguientes
        )
        
    def analizar(self, tokens):
        """Analiza una lista de tokens usando la tabla LL(1)"""
        self.errores = []
        return self.analizador_ll1.analizar(
            tokens, self.tabla_ll1, self.primeros, self.siguientes
        )
        
    def obtener_errores(self):
        """Retorna la lista de errores encontrados"""
        return self.analizador_ll1.errores
        
    def inicializar(self):
        """Inicializa el analizador calculando primeros, siguientes y tabla LL(1)"""
        print("Calculando conjuntos PRIMEROS...")
        self.calcular_primeros()
        
        print("Calculando conjuntos SIGUIENTES...")
        self.calcular_siguientes()
        
        print("Construyendo tabla LL(1)...")
        self.construir_tabla_ll1()
        
        print("Analizador sintáctico inicializado correctamente")
        
    def mostrar_conjuntos(self):
        """Muestra los conjuntos PRIMEROS y SIGUIENTES"""
        print("\nConjuntos PRIMEROS:")
        for simbolo in sorted(self.primeros.keys()):
            if simbolo in self.no_terminales:
                print(f"PRIMEROS({simbolo}) = {{{', '.join(sorted(self.primeros[simbolo]))}}}")
        
        print("\nConjuntos SIGUIENTES:")
        for simbolo in sorted(self.siguientes.keys()):
            print(f"SIGUIENTES({simbolo}) = {{{', '.join(sorted(self.siguientes[simbolo]))}}}")
