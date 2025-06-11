# -*- coding: utf-8 -*-
"""
Utilidades del analizador sintáctico
Contiene funciones de utilidad para el análisis sintáctico
"""

from .sintacticomain import AnalizadorSintactico
from .ast_builder import ASTBuilder


def analizar_sintacticamente(tokens):
    """Función principal para análisis sintáctico"""
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    exito, arbol = analizador.analizar(tokens)
    
    if exito:
        print("\n" + "="*50)
        print("ÁRBOL SINTÁCTICO:")
        print("="*50)
        arbol.mostrar_arbol()
        
        # Construir el AST
        ast_builder = ASTBuilder()
        ast = ast_builder.construir_ast(arbol)
        
        print("\n" + "="*50)
        print("ÁRBOL SINTÁCTICO ABSTRACTO (AST):")
        print("="*50)
        ast.mostrar_arbol()
        
        return True, arbol, ast
    else:
        return False, None, None


def leer_tokens_desde_archivo(archivo_path):
    """Lee tokens desde un archivo de texto con formato: tipo lexema linea columna"""
    tokens = []
    try:
        with open(archivo_path, 'r', encoding='utf-8') as file:
            for linea_num, linea in enumerate(file, 1):
                linea = linea.strip()
                if linea and not linea.startswith('#'):  # Ignorar líneas vacías y comentarios
                    partes = linea.split('\t')  # Asumiendo separación por tabulación
                    if len(partes) >= 4:
                        tipo = partes[0]
                        lexema = partes[1]
                        linea_token = int(partes[2])
                        columna_token = int(partes[3])
                        tokens.append((tipo, lexema, linea_token, columna_token))
                    else:
                        # Intento con separación por espacios
                        partes = linea.split()
                        if len(partes) >= 4:
                            tipo = partes[0]
                            lexema = partes[1]
                            linea_token = int(partes[2])
                            columna_token = int(partes[3])
                            tokens.append((tipo, lexema, linea_token, columna_token))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_path}")
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
    
    return tokens


def analizar_sintacticamente_desde_archivo(archivo_tokens):
    """Función principal para análisis sintáctico desde archivo"""
    tokens = leer_tokens_desde_archivo(archivo_tokens)
    
    if not tokens:
        print("No se pudieron leer tokens del archivo")
        return False, None, None, []
    
    analizador = AnalizadorSintactico()
    analizador.inicializar()
    
    exito, arbol = analizador.analizar(tokens)
    errores = analizador.obtener_errores()
    
    if exito:
        # Construir el AST
        ast_builder = ASTBuilder()
        ast = ast_builder.construir_ast(arbol)
        return exito, arbol, ast, errores
    else:
        return exito, arbol, None, errores
