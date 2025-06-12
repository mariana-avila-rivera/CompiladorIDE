#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar los cambios en la visualización del árbol
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analizadores.sintactico.tree_visualization import TreeVisualizationWidget
from analizadores.sintactico.arbol_sintactico import NodoArbol

def crear_arbol_prueba():
    """Crea un árbol de prueba más completo que simule el código real"""
    
    # Crear el nodo raíz del programa
    programa = NodoArbol('programa')
    
    # main {
    main_token = NodoArbol('main')
    main_token.token_info = {'tipo': 'Palabra reservada', 'linea': 1, 'columna': 1}
    programa.agregar_hijo(main_token)
    
    llave_abrir = NodoArbol('{')
    llave_abrir.token_info = {'tipo': 'Símbolo', 'linea': 1, 'columna': 6}
    programa.agregar_hijo(llave_abrir)
    
    # Crear declaración de variable: int contador, limite;
    decl_var = NodoArbol('declaracion_variable')
    programa.agregar_hijo(decl_var)
    
    tipo_int = NodoArbol('int')
    tipo_int.token_info = {'tipo': 'Palabra reservada', 'linea': 2, 'columna': 5}
    decl_var.agregar_hijo(tipo_int)
    
    id_contador = NodoArbol('contador')
    id_contador.token_info = {'tipo': 'Identificador', 'linea': 2, 'columna': 9}
    decl_var.agregar_hijo(id_contador)
    
    id_limite = NodoArbol('limite')
    id_limite.token_info = {'tipo': 'Identificador', 'linea': 2, 'columna': 19}
    decl_var.agregar_hijo(id_limite)
    
    # Declaración float promedio, suma;
    decl_var2 = NodoArbol('declaracion_variable')
    programa.agregar_hijo(decl_var2)
    
    tipo_float = NodoArbol('float')
    tipo_float.token_info = {'tipo': 'Palabra reservada', 'linea': 3, 'columna': 5}
    decl_var2.agregar_hijo(tipo_float)
    
    id_promedio = NodoArbol('promedio')
    id_promedio.token_info = {'tipo': 'Identificador', 'linea': 3, 'columna': 11}
    decl_var2.agregar_hijo(id_promedio)
    
    id_suma = NodoArbol('suma')
    id_suma.token_info = {'tipo': 'Identificador', 'linea': 3, 'columna': 21}
    decl_var2.agregar_hijo(id_suma)
    
    # Asignación: limite = 10;
    asignacion1 = NodoArbol('asignacion')
    programa.agregar_hijo(asignacion1)
    
    id_limite2 = NodoArbol('limite')
    id_limite2.token_info = {'tipo': 'Identificador', 'linea': 5, 'columna': 5}
    asignacion1.agregar_hijo(id_limite2)
    
    op_igual = NodoArbol('=')
    op_igual.token_info = {'tipo': 'Operador de asignación', 'linea': 5, 'columna': 12}
    asignacion1.agregar_hijo(op_igual)
    
    numero_10 = NodoArbol('10')
    numero_10.token_info = {'tipo': 'Número entero', 'linea': 5, 'columna': 14}
    asignacion1.agregar_hijo(numero_10)
    
    # Asignación con expresión: suma = x + 56;
    asignacion2 = NodoArbol('asignacion')
    programa.agregar_hijo(asignacion2)
    
    id_suma2 = NodoArbol('suma')
    id_suma2.token_info = {'tipo': 'Identificador', 'linea': 6, 'columna': 5}
    asignacion2.agregar_hijo(id_suma2)
    
    op_igual2 = NodoArbol('=')
    op_igual2.token_info = {'tipo': 'Operador de asignación', 'linea': 6, 'columna': 9}
    asignacion2.agregar_hijo(op_igual2)
    
    # Expresión x + 56
    expresion = NodoArbol('expresion_simple')
    asignacion2.agregar_hijo(expresion)
    
    id_x = NodoArbol('x')
    id_x.token_info = {'tipo': 'Identificador', 'linea': 6, 'columna': 11}
    expresion.agregar_hijo(id_x)
    
    op_suma = NodoArbol('+')
    op_suma.token_info = {'tipo': 'Operador aritmético', 'linea': 6, 'columna': 13}
    expresion.agregar_hijo(op_suma)
    
    numero_56 = NodoArbol('56')
    numero_56.token_info = {'tipo': 'Número entero', 'linea': 6, 'columna': 15}
    expresion.agregar_hijo(numero_56)
    
    # Sentencia if
    seleccion = NodoArbol('seleccion')
    programa.agregar_hijo(seleccion)
    
    if_token = NodoArbol('if')
    if_token.token_info = {'tipo': 'Palabra reservada', 'linea': 13, 'columna': 5}
    seleccion.agregar_hijo(if_token)
    
    # Condición: contador < limite
    expresion_cond = NodoArbol('expresion')
    seleccion.agregar_hijo(expresion_cond)
    
    id_contador2 = NodoArbol('contador')
    id_contador2.token_info = {'tipo': 'Identificador', 'linea': 13, 'columna': 9}
    expresion_cond.agregar_hijo(id_contador2)
    
    op_menor = NodoArbol('<')
    op_menor.token_info = {'tipo': 'Operador relacional', 'linea': 13, 'columna': 18}
    expresion_cond.agregar_hijo(op_menor)
    
    id_limite3 = NodoArbol('limite')
    id_limite3.token_info = {'tipo': 'Identificador', 'linea': 13, 'columna': 20}
    expresion_cond.agregar_hijo(id_limite3)
    
    # Then
    then_token = NodoArbol('then')
    then_token.token_info = {'tipo': 'Palabra reservada', 'linea': 13, 'columna': 28}
    seleccion.agregar_hijo(then_token)
    
    # cout << contador;
    sent_out = NodoArbol('sent_out')
    seleccion.agregar_hijo(sent_out)
    
    cout_token = NodoArbol('cout')
    cout_token.token_info = {'tipo': 'Palabra reservada', 'linea': 14, 'columna': 9}
    sent_out.agregar_hijo(cout_token)
    
    op_shift = NodoArbol('<<')
    op_shift.token_info = {'tipo': 'Operador de shift', 'linea': 14, 'columna': 14}
    sent_out.agregar_hijo(op_shift)
    
    id_contador3 = NodoArbol('contador')
    id_contador3.token_info = {'tipo': 'Identificador', 'linea': 14, 'columna': 17}
    sent_out.agregar_hijo(id_contador3)
    
    # }
    llave_cerrar = NodoArbol('}')
    llave_cerrar.token_info = {'tipo': 'Símbolo', 'linea': 19, 'columna': 1}
    programa.agregar_hijo(llave_cerrar)
    
    # ;
    punto_coma = NodoArbol(';')
    punto_coma.token_info = {'tipo': 'Símbolo', 'linea': 19, 'columna': 2}
    programa.agregar_hijo(punto_coma)
    
    return programa

def main():
    """Función principal para probar la visualización"""
    
    # Crear ventana de prueba
    root = tk.Tk()
    root.title("Prueba - Estructura del Programa con Terminales Organizados")
    root.geometry("900x700")
    
    # Crear widget de visualización
    tree_widget = TreeVisualizationWidget(root)
    
    # Crear árbol de prueba
    arbol_prueba = crear_arbol_prueba()
    
    # Mostrar el árbol
    tree_widget.mostrar_arbol(arbol_prueba)
    
    # Agregar botón para limpiar
    btn_frame = tk.Frame(root)
    btn_frame.pack(side=tk.BOTTOM, pady=5)
    
    def limpiar_arbol():
        tree_widget.limpiar()
    
    def mostrar_arbol():
        tree_widget.mostrar_arbol(arbol_prueba)
    
    btn_limpiar = tk.Button(btn_frame, text="Limpiar", command=limpiar_arbol)
    btn_limpiar.pack(side=tk.LEFT, padx=5)
    
    btn_mostrar = tk.Button(btn_frame, text="Mostrar Árbol", command=mostrar_arbol)
    btn_mostrar.pack(side=tk.LEFT, padx=5)
    
    # Agregar texto explicativo
    info_label = tk.Label(root, text="Estructura: { (raíz) → declaraciones y asignaciones → operadores engloban operandos", 
                         bg="lightgray", anchor="w")
    info_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
