def resaltar_palabras(text_area):
    # Limpiar todos los tags existentes
    for tag in text_area.tag_names():
        text_area.tag_remove(tag, "1.0", "end")

    # Configurar todos los tags de colores
    text_area.tag_config("comment_tag",
                         foreground="#1F642B")  # Comentarios
    text_area.tag_config("number_tag",
                         foreground="#0022FF")  # Números
    text_area.tag_config("keyword_tag",
                         foreground="#800080")  # Palabras reservadas
    text_area.tag_config("arithmetic_tag",
                         foreground="#958E12")  # Operadores aritméticos
    text_area.tag_config("logical_tag",
                         foreground="#763A58")  # Op. lógicos y relacionales
    text_area.tag_config("symbol_tag",
                         foreground="#FF00FF")  # Símbolos
    text_area.tag_config("assign_tag",
                         foreground="#1FBB9A")  # Asignación

    # Colecciones de tokens por categoría
    keywords = {"if", "then", "else", "end", "do", "while",
                "switch", "case", "int", "float", "real",
                "main", "cin", "cout", "until"}
    arithmetic_ops_single = {"*", "/", "%", "^"}
    arithmetic_ops_plus_minus = {"+", "-"}  # Separamos + y -
    logical_words = {"and", "or", "not", "AND", "OR", "NOT"}
    assign_ops = {"=", "+=", "-=", "*=", "/=", "%=", "^="}
    symbols = {"(", ")", "{", "}", "[", "]", ";", ","}

    # Tratar el texto completo primero para comentarios
    marcar_comentarios_primero(text_area)

    # La posición de análisis comienza desde el principio
    pos = "1.0"

    while text_area.compare(pos, "<", "end"):
        # Si estamos en un comentario, saltamos a la siguiente posición que no es comentario
        if "comment_tag" in text_area.tag_names(pos):
            # Encontrar el final del comentario
            next_pos = pos
            while text_area.compare(next_pos, "<", "end") and "comment_tag" in text_area.tag_names(next_pos):
                next_pos = text_area.index(f"{next_pos}+1c")
            pos = next_pos
            continue

        char = text_area.get(pos)

        # Si estamos en el final del texto, salimos
        if not char:
            break

        # Obtener el siguiente carácter si existe
        next_pos = text_area.index(f"{pos}+1c") if text_area.compare(pos, "<", "end-1c") else "end"
        next_char = text_area.get(next_pos) if text_area.compare(next_pos, "<", "end") else ""

        # Verificar números (enteros y flotantes)
        if char.isdigit() or (char in '+-' and next_char.isdigit() and
                               (pos == "1.0" or not text_area.get(f"{pos}-1c").isalnum())):
            start_pos = pos
            pos = procesar_numero(text_area, pos)
            continue

        # Verificar palabras reservadas y palabras lógicas
        if char.isalpha() or char == '_':
            start_pos = pos
            word, pos = obtener_palabra_completa(text_area, pos)

            if word.lower() in logical_words:
                text_area.tag_add("logical_tag", start_pos, pos)
            elif word in keywords:
                text_area.tag_add("keyword_tag", start_pos, pos)

            continue

        # Verificar operadores de incremento/decremento (++ y --)
        if (char == "+" and next_char == "+") or (char == "-" and next_char == "-"):
            text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            continue

        # Verificar operadores relacionales (==, !=, <=, >=)
        if ((char in "=!<>" and next_char == "=") or
            (char in "<>" and next_char == "=")):
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            continue

        # Verificar operadores lógicos (&&, ||)
        if (char == "&" and next_char == "&") or (char == "|" and next_char == "|"):
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            continue

        # Verificar operadores de asignación compuestos (+=, -=, *=, /=, %=, ^=)
        if char in arithmetic_ops_single and next_char == "=":
            text_area.tag_add("assign_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            continue

        # Verificar operador de asignación simple (=). "+=", "-=", "*=", "/=", "%=", "^="     
        if char == "=" or (char in arithmetic_ops_plus_minus and next_char == "=") or (char in arithmetic_ops_single and next_char == "="):
            text_area.tag_add("assign_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue

        # Verificar operadores aritméticos de un carácter (*, /, %, ^)
        if char in arithmetic_ops_single:
            text_area.tag_add("arithmetic_tag", pos,
                              text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue

        # Verificar operadores aritméticos de un carácter (+, -)
        if char in arithmetic_ops_plus_minus:
            # Se considera parte de un número solo si...
            es_signo_de_numero = False
            if next_char.isdigit():
                prev_pos = text_area.index(f"{pos}-1c") if text_area.compare("1.0", "<", pos) else None
                prev_char = text_area.get(prev_pos) if prev_pos else None

                if prev_char is None or not prev_char.isalnum():
                    es_signo_de_numero = True

            if es_signo_de_numero:
                start_pos = pos
                pos = procesar_numero(text_area, pos)
                continue
            else:
                text_area.tag_add("arithmetic_tag", pos,
                                  text_area.index(f"{pos}+1c"))
                pos = text_area.index(f"{pos}+1c")
                continue

        # Verificar operadores relacionales de un carácter (<, >)
        if char in "<>":
            text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue

        # Verificar símbolos
        if char in symbols:
            text_area.tag_add("symbol_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue

        # Avanzar si no se aplica ninguna regla
        pos = text_area.index(f"{pos}+1c")


def marcar_comentarios_primero(text_area):
    # Marca todos los comentarios primero para darles prioridad
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


def procesar_numero(text_area, pos):
    # Procesa y marca un número (entero o decimal)
    start_pos = pos
    char = text_area.get(pos)

    # Manejar signo inicial
    if char in '+-':
        pos = text_area.index(f"{pos}+1c")

    tiene_punto = False
    while text_area.compare(pos, "<", "end"):
        char = text_area.get(pos)
        if char.isdigit():
            pos = text_area.index(f"{pos}+1c")
        elif char == '.' and not tiene_punto:
            tiene_punto = True
            pos = text_area.index(f"{pos}+1c")
        else:
            break

    text_area.tag_add("number_tag", start_pos, pos)
    return pos


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
