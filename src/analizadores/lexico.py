def resaltar_palabras(text_area):
    # Limpiar todos los tags existentes
    for tag in text_area.tag_names():
        text_area.tag_remove(tag, "1.0", "end")

    # Configurar todos los tags de colores (sin cambios)
    text_area.tag_config("comment_tag", foreground="#1F642B")
    text_area.tag_config("number_tag", foreground="#0022FF")
    text_area.tag_config("keyword_tag", foreground="#800080")
    text_area.tag_config("arithmetic_tag", foreground="#958E12")
    text_area.tag_config("logical_tag", foreground="#763A58")
    text_area.tag_config("symbol_tag", foreground="#FF00FF")
    text_area.tag_config("assign_tag", foreground="#1FBB9A")

    # Colecciones de tokens
    keywords = {"if", "then", "else", "end", "do", "while", "switch", "case", "int", "float", "real", "main", "cin", "cout", "until"}
    arithmetic_ops_single = {"*", "/", "%", "^"}
    arithmetic_ops_plus_minus = {"+", "-"}
    logical_words = {"and", "or", "not", "AND", "OR", "NOT"}
    assign_ops = {"=", "+=", "-=", "*=", "/=", "%=", "^="}
    symbols = {"(", ")", "{", "}", "[", "]", ";", ","}
    relational_ops_single = {"<", ">"} # Añadimos < y > aquí

    # Lista para almacenar los errores léxicos encontrados
    errores_lexicos = []

    # Tratar el texto completo primero para comentarios
    marcar_comentarios_primero(text_area)

    # La posición de análisis comienza desde el principio
    pos = "1.0"

    while text_area.compare(pos, "<", "end"):
        # Obtener la línea y columna actuales desde la posición del texto
        # Formato de pos: "linea.columna"
        pos_parts = pos.split(".")
        fila = int(pos_parts[0])
        columna = int(pos_parts[1]) + 1  # +1 porque la columna en el widget comienza en 0
        
        char = text_area.get(pos)

        # Obtener el siguiente carácter si existe
        next_pos = text_area.index(f"{pos}+1c") if text_area.compare(pos, "<", "end-1c") else "end"
        next_char = text_area.get(next_pos) if text_area.compare(next_pos, "<", "end") else ""

        # Si estamos en un comentario, saltamos
        if "comment_tag" in text_area.tag_names(pos):
            pos = text_area.index(f"{pos}+1c")
            continue

        token_reconocido = False
        avanzar = 1 # Cantidad de caracteres para avanzar por defecto

        # Verificar números
        if char.isdigit() or (char in '+-' and next_char.isdigit() and
                               (pos == "1.0" or not text_area.get(f"{pos}-1c").isalnum())):
            start_pos = pos
            pos, num_errors = procesar_numero(text_area, pos, fila, columna, errores_lexicos)
            token_reconocido = True
            continue

        # Verificar palabras clave y lógicas
        if char.isalpha() or char == '_':
            start_pos = pos
            word, pos = obtener_palabra_completa(text_area, pos)
            if word.lower() in logical_words or word in keywords:
                if word.lower() in logical_words:
                    text_area.tag_add("logical_tag", start_pos, pos)
                else:
                    text_area.tag_add("keyword_tag", start_pos, pos)
                token_reconocido = True
            else:
                token_reconocido = True # Consideramos identificadores válidos por ahora
            continue

        # Verificar operadores de incremento/decremento
        if (char == "+" and next_char == "+") or (char == "-" and next_char == "-"):
            text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            avanzar = 2
            continue

        # Verificar operadores relacionales de dos caracteres
        if ((char in "=!<>" and next_char == "=") or
            (char in "<>" and next_char == "=")):
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            avanzar = 2
            continue

        # Verificar operadores lógicos
        if (char == "&" and next_char == "&") or (char == "|" and next_char == "|"):
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            avanzar = 2
            continue

        # Verificar operadores de asignación
        if char == "=" or (char in arithmetic_ops_single and next_char == "=") or \
           (char in arithmetic_ops_plus_minus and next_char == "="):
            text_area.tag_add("assign_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue

        # Verificar operadores aritméticos simples
        if char in arithmetic_ops_single:
            text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue

        # Verificar operadores aritméticos + y -
        if char in arithmetic_ops_plus_minus:
            es_signo_de_numero = False
            if next_char.isdigit():
                prev_pos = text_area.index(f"{pos}-1c") if text_area.compare("1.0", "<", pos) else None
                prev_char = text_area.get(prev_pos) if prev_pos else None
                if prev_char is None or not prev_char.isalnum():
                    es_signo_de_numero = True
            if es_signo_de_numero:
                start_pos = pos
                pos, num_errors = procesar_numero(text_area, pos, fila, columna, errores_lexicos)
            else:
                text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+1c"))
                pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue

        # Verificar operadores relacionales de un carácter
        if char in relational_ops_single:
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue

        # Verificar símbolos
        if char in symbols:
            text_area.tag_add("symbol_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue

        # Si no se reconoce ningún token, es un error de carácter inválido
        if not token_reconocido and char.strip():
            error_msg = f"Error léxico: Carácter inválido '{char}' en Fila {fila}, Columna {columna}"
            errores_lexicos.append(error_msg)
            pos = text_area.index(f"{pos}+1c")
            continue
        elif not token_reconocido:
            pos = text_area.index(f"{pos}+1c")
            continue
    
    # Retornar la lista de errores léxicos
    return errores_lexicos


def marcar_comentarios_primero(text_area):
    # Marca todos los comentarios primero para darles prioridad"""
    # Buscar comentarios de línea (//)
    pos = "1.0"
    while True:
        pos = text_area.search("//", pos, stopindex="end", nocase=False)
        if not pos:
            break
        # El comentario se extiende hasta el final de la línea
        line = pos.split('.')[0]
        end_pos = text_area.index(f"{line}.end")
        text_area.tag_add("comment_tag", pos, end_pos)
        pos = end_pos  # Continuar desde el final de este comentario

    # Buscar comentarios de bloque (/* */)
    pos = "1.0"
    while True:
        pos = text_area.search("/*", pos, stopindex="end", nocase=False)
        if not pos:
            break
        start_pos = pos
        pos = text_area.index(f"{pos}+2c")  # Saltar /*

        # Buscar el cierre */
        end_pos = text_area.search("*/", pos, stopindex="end", nocase=False)
        if not end_pos:
            # Si no hay cierre, marcar hasta el final
            text_area.tag_add("comment_tag", start_pos, "end")
            break
        else:
            end_pos = text_area.index(f"{end_pos}+2c")  # Incluir */
            text_area.tag_add("comment_tag", start_pos, end_pos)
            pos = end_pos  # Continuar desde el final del comentario


def procesar_numero(text_area, pos, fila, columna, errores_lexicos):
    # Procesa y marca un número (entero o decimal) y detecta errores
    start_pos = pos
    tiene_punto = False
    pos_inicial = pos
    char = text_area.get(pos)
    numero_completo = ""

    # Manejar signo inicial
    if char in '+-':
        numero_completo += char
        pos = text_area.index(f"{pos}+1c")
        # Actualizar la columna para el mensaje de error
        pos_parts = pos.split(".")
        columna_actual = int(pos_parts[1]) + 1

        if not text_area.compare(pos, "<", "end") or not text_area.get(pos).isdigit():
            error_msg = f"Error léxico: Signo '{char}' sin número siguiente en Fila {fila}, Columna {columna}"
            errores_lexicos.append(error_msg)
            return pos, 1  # Retornar posición y número de errores

    while text_area.compare(pos, "<", "end"):
        char = text_area.get(pos)
        # Obtener la posición actual para mensajes de error
        pos_parts = pos.split(".")
        fila_actual = int(pos_parts[0])
        columna_actual = int(pos_parts[1]) + 1
        
        if char.isdigit():
            numero_completo += char
            pos = text_area.index(f"{pos}+1c")
        elif char == '.' and not tiene_punto:
            tiene_punto = True
            numero_completo += char
            pos = text_area.index(f"{pos}+1c")
            
            # Verificar si el siguiente carácter después del punto es un dígito
            if text_area.compare(pos, "<", "end"):
                next_char_after_dot = text_area.get(pos)
                if not next_char_after_dot.isdigit():
                    # Error: punto seguido de no dígito
                    error_msg = f"Error léxico: Carácter inválido '{numero_completo}' en Fila {fila_actual}, Columna {columna_actual}"
                    errores_lexicos.append(error_msg)
                    break # Detener el procesamiento del número
            else:
                # Error: punto al final del texto
                error_msg = f"Error léxico: Carácter inválido '{numero_completo}' en Fila {fila_actual}, Columna {columna_actual}"
                errores_lexicos.append(error_msg)
                break
        else:
            break

    text_area.tag_add("number_tag", start_pos, pos)
    return pos, 0  # Retornar posición y número de errores (0 si no hubo errores)

def obtener_palabra_completa(text_area, pos):
    # Obtiene una palabra completa desde la posición actual
    word = ""

    while text_area.compare(pos, "<", "end"):
        char = text_area.get(pos)
        if char.isalnum() or char == '_':
            word += char
            pos = text_area.index(f"{pos}+1c")
        else:
            break

    return word, pos

def tokenizar_codigo(text_area):
    """
    Analiza el texto en el área de texto y genera una lista de tokens encontrados.
    Cada token incluye su tipo, valor, línea y columna.
    """
    # Listas para almacenar los tokens
    tokens = []
    
    # Colecciones de tokens
    keywords = {"if", "then", "else", "end", "do", "while", "switch", "case", "int", "float", "real", "main", "cin", "cout", "until"}
    arithmetic_ops_single = {"*", "/", "%", "^"}
    arithmetic_ops_plus_minus = {"+", "-"}
    logical_words = {"and", "or", "not", "AND", "OR", "NOT"}
    assign_ops = {"=", "+=", "-=", "*=", "/=", "%=", "^="}
    symbols = {"(", ")", "{", "}", "[", "]", ";", ","}
    relational_ops_single = {"<", ">"}
    
    # Primero marcamos los comentarios para poder ignorarlos
    text_area_temp = text_area
    marcar_comentarios_primero(text_area_temp)
    
    # La posición de análisis comienza desde el principio
    pos = "1.0"
    
    while text_area.compare(pos, "<", "end"):
        # Obtener la línea y columna actuales desde la posición del texto
        pos_parts = pos.split(".")
        fila = int(pos_parts[0])
        columna = int(pos_parts[1]) + 1  # +1 porque la columna en el widget comienza en 0
        
        char = text_area.get(pos)
        
        # Obtener el siguiente carácter si existe
        next_pos = text_area.index(f"{pos}+1c") if text_area.compare(pos, "<", "end-1c") else "end"
        next_char = text_area.get(next_pos) if text_area.compare(next_pos, "<", "end") else ""
        
        # Si estamos en un comentario, saltamos
        if "comment_tag" in text_area.tag_names(pos):
            pos = text_area.index(f"{pos}+1c")
            continue
        
        token_reconocido = False
        
        # Si encontramos un ';', procesamos los operadores + y - acumulados
        if char == ';':
            tokens.append(("Símbolo", char, fila, columna))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar operadores de incremento/decremento
        if (char == "+" and next_char == "+") or (char == "-" and next_char == "-"):
            tokens.append(("Operador aritmético", char + next_char, fila, columna))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            continue
        
        # Verificar operadores + y - individuales
        if char in arithmetic_ops_plus_minus:
            # Verificar si es un signo de número
            if next_char.isdigit() and (pos == "1.0" or not text_area.get(f"{pos}-1c").isalnum()):
                # Es un signo de número, procesamos el número completo
                start_pos = pos
                valor_token = char
                pos = text_area.index(f"{pos}+1c")
                char = text_area.get(pos) if text_area.compare(pos, "<", "end") else ""
                
                # Procesar la parte entera del número
                while text_area.compare(pos, "<", "end") and char.isdigit():
                    valor_token += char
                    pos = text_area.index(f"{pos}+1c")
                    if text_area.compare(pos, "<", "end"):
                        char = text_area.get(pos)
                    else:
                        break
                
                # Verificar si hay un punto decimal
                if text_area.compare(pos, "<", "end") and char == '.':
                    next_pos_after_dot = text_area.index(f"{pos}+1c") if text_area.compare(pos, "<", "end-1c") else "end"
                    next_char_after_dot = text_area.get(next_pos_after_dot) if text_area.compare(next_pos_after_dot, "<", "end") else ""
                    
                    if next_char_after_dot.isdigit():
                        # Es un número real válido
                        valor_token += char
                        pos = text_area.index(f"{pos}+1c")
                        char = text_area.get(pos)
                        
                        # Procesar la parte decimal
                        while text_area.compare(pos, "<", "end") and char.isdigit():
                            valor_token += char
                            pos = text_area.index(f"{pos}+1c")
                            if text_area.compare(pos, "<", "end"):
                                char = text_area.get(pos)
                            else:
                                break
                        
                        tokens.append(("Número real", valor_token, fila, columna))
                    else:
                        # Es un número entero seguido de un punto que no forma parte del número
                        # No lo agregamos a tokens ya que es un error
                        pass
                else:
                    # Es un número entero sin punto
                    tokens.append(("Número entero", valor_token, fila, columna))
            else:
                # Es un operador aritmético
                tokens.append(("Operador aritmético", char, fila, columna))
                pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar si es un punto suelto (no parte de un número)
        if char == '.' and (next_char == '' or not next_char.isdigit()) and (pos == "1.0" or not text_area.get(f"{pos}-1c").isdigit()):
            # Es un punto suelto, lo ignoramos (no lo agregamos a tokens)
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar números
        if char.isdigit():
            start_pos = pos
            valor_token = ""
            
            # Procesar la parte entera del número
            while text_area.compare(pos, "<", "end") and char.isdigit():
                valor_token += char
                pos = text_area.index(f"{pos}+1c")
                if text_area.compare(pos, "<", "end"):
                    char = text_area.get(pos)
                else:
                    break
            
            # Verificar si hay un punto decimal
            if text_area.compare(pos, "<", "end") and char == '.':
                next_pos_after_dot = text_area.index(f"{pos}+1c") if text_area.compare(pos, "<", "end-1c") else "end"
                next_char_after_dot = text_area.get(next_pos_after_dot) if text_area.compare(next_pos_after_dot, "<", "end") else ""
                
                if next_char_after_dot.isdigit():
                    # Es un número real válido
                    valor_token += char
                    pos = text_area.index(f"{pos}+1c")
                    char = text_area.get(pos)
                    
                    # Procesar la parte decimal
                    while text_area.compare(pos, "<", "end") and char.isdigit():
                        valor_token += char
                        pos = text_area.index(f"{pos}+1c")
                        if text_area.compare(pos, "<", "end"):
                            char = text_area.get(pos)
                        else:
                            break
                    
                    tokens.append(("Número real", valor_token, fila, columna))
                else:
                    # Es un número entero seguido de un punto que no forma parte del número
                    # No lo agregamos a tokens ya que es un error
                    pass
            else:
                # Es un número entero sin punto
                tokens.append(("Número entero", valor_token, fila, columna))
            
            token_reconocido = True
            continue
        
        # Verificar palabras clave, lógicas e identificadores
        if char.isalpha() or char == '_':
            start_pos = pos
            word, pos = obtener_palabra_completa(text_area, pos)
            
            if word in keywords:
                tokens.append(("Palabra reservada", word, fila, columna))
            elif word.lower() in logical_words:
                tokens.append(("Operador lógico", word, fila, columna))
            else:
                tokens.append(("Identificador", word, fila, columna))
            
            token_reconocido = True
            continue
        
        # Verificar operadores relacionales de dos caracteres
        if ((char in "=!<>" and next_char == "=") or
            (char in "<>" and next_char == "=")):
            
            tokens.append(("Operador relacional", char + next_char, fila, columna))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            continue
        
        # Verificar operadores lógicos
        if (char == "&" and next_char == "&") or (char == "|" and next_char == "|"):
            
            tokens.append(("Operador lógico", char + next_char, fila, columna))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            continue
        
        # Verificar operadores de asignación
        if (char in arithmetic_ops_single or char in arithmetic_ops_plus_minus) and next_char == "=":
            
            tokens.append(("Operador de asignación", char + next_char, fila, columna))
            pos = text_area.index(f"{pos}+2c")
            token_reconocido = True
            continue
        elif char == "=":
            
            tokens.append(("Operador de asignación", char, fila, columna))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar operadores aritméticos simples
        if char in arithmetic_ops_single:
            
            tokens.append(("Operador aritmético", char, fila, columna))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar operadores relacionales de un carácter
        if char in relational_ops_single:
            
            tokens.append(("Operador relacional", char, fila, columna))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Verificar símbolos
        if char in symbols:
            
            tokens.append(("Símbolo", char, fila, columna))
            pos = text_area.index(f"{pos}+1c")
            token_reconocido = True
            continue
        
        # Si no reconocimos ningún token, avanzamos
        if not token_reconocido:
            pos = text_area.index(f"{pos}+1c")
    
    return tokens

def procesar_operadores_acumulados(chars_acumulados, tokens):
    """
    Procesa los operadores + y - acumulados y los agrupa en pares
    """
    i = 0
    while i < len(chars_acumulados):
        if i + 1 < len(chars_acumulados):
            # Tenemos un par
            char1, fila1, columna1 = chars_acumulados[i]
            char2, fila2, columna2 = chars_acumulados[i+1]
            tokens.append(("Operador aritmético", char1 + char2, fila1, columna1))
            i += 2
        else:
            # Solo queda un operador
            char, fila, columna = chars_acumulados[i]
            tokens.append(("Operador aritmético", char, fila, columna))
            i += 1
