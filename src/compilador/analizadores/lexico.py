def resaltar_palabras(text_area):
    # Limpiar todos los tags existentes
    for tag in text_area.tag_names():
        text_area.tag_remove(tag, "1.0", "end")
    
    # Configurar todos los tags de colores
    text_area.tag_config("comment_tag", foreground="#1F642B")    # Comentarios
    text_area.tag_config("number_tag", foreground="#0022FF")     # Números
    text_area.tag_config("keyword_tag", foreground="#800080")    # Palabras reservadas
    text_area.tag_config("arithmetic_tag", foreground="#958E12") # Operadores aritméticos
    text_area.tag_config("logical_tag", foreground="#763A58")    # Operadores lógicos
    text_area.tag_config("symbol_tag", foreground="#FF00FF")     # Símbolos
    text_area.tag_config("assign_tag", foreground="#1FBB9A")     # Asignación
    
    # Palabras clave por categoría
    keywords = {"if", "then", "else", "end", "do", "while", "switch", "case", "int", "float", "main", "cin", "cout"}
    
    # Posición global de análisis
    pos = "1.0"
    last_pos = text_area.index("end-1c")
    
    # Analizar todo el texto caracter por caracter
    while text_area.compare(pos, "<", "end"):
        # Obtener el carácter actual y el siguiente
        char = text_area.get(pos)
        next_pos = text_area.index(f"{pos}+1c")
        next_char = text_area.get(next_pos) if text_area.compare(next_pos, "<", "end") else ""
        
        # Verificar comentarios primero (mayor prioridad)
        if char == "/" and next_char == "/":  # Comentario de línea
            line_start = pos.split('.')[0]
            end_pos = text_area.index(f"{line_start}.end")
            text_area.tag_add("comment_tag", pos, end_pos)
            pos = end_pos  # Saltar al final de la línea
            continue
            
        elif char == "/" and next_char == "*":  # Comentario de bloque
            start_pos = pos
            pos = text_area.index(f"{pos}+2c")  # Saltar los primeros dos caracteres "/*"
            
            # Buscar el cierre "*/"
            found_end = False
            while not found_end and text_area.compare(pos, "<", "end"):
                curr_char = text_area.get(pos)
                next_pos = text_area.index(f"{pos}+1c")
                next_char = text_area.get(next_pos) if text_area.compare(next_pos, "<", "end") else ""
                
                if curr_char == "*" and next_char == "/":
                    end_pos = text_area.index(f"{pos}+2c")  # Incluir "*/"
                    text_area.tag_add("comment_tag", start_pos, end_pos)
                    pos = end_pos
                    found_end = True
                else:
                    pos = text_area.index(f"{pos}+1c")
            
            if not found_end:  # Si no se encontró cierre, marcar hasta el final
                text_area.tag_add("comment_tag", start_pos, "end")
                pos = text_area.index("end")
            continue
        
        # Verificar números
        if char.isdigit() or (char in '+-' and next_char.isdigit()):
            start_pos = pos
            if char in '+-':
                pos = text_area.index(f"{pos}+1c")
                
            tiene_punto = False
            while text_area.compare(pos, "<", "end"):
                current_char = text_area.get(pos)
                if current_char.isdigit():
                    pos = text_area.index(f"{pos}+1c")
                elif current_char == '.' and not tiene_punto:
                    tiene_punto = True
                    pos = text_area.index(f"{pos}+1c")
                else:
                    break
            
            text_area.tag_add("number_tag", start_pos, pos)
            continue
        
        # Verificar palabras reservadas
        if char.isalpha():
            start_pos = pos
            word = ""
            
            # Extraer la palabra completa
            while text_area.compare(pos, "<", "end"):
                current_char = text_area.get(pos)
                if current_char.isalnum() or current_char == '_':
                    word += current_char
                    pos = text_area.index(f"{pos}+1c")
                else:
                    break
            
            # Verificar si es una palabra clave
            if word in keywords:
                text_area.tag_add("keyword_tag", start_pos, pos)
                continue
        
        # Verificar operadores aritméticos
        if char in {"+", "-", "*", "/", "%", "^", "++", "--"}:
            start_pos = pos
            if char in "+-" and next_char == char:  # ++, --
                text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+2c"))
                pos = text_area.index(f"{pos}+2c")
            else:
                text_area.tag_add("arithmetic_tag", pos, text_area.index(f"{pos}+1c"))
                pos = text_area.index(f"{pos}+1c")
            continue
        
        # Verificar operadores lógicos y relacionales
        if char in  {"==", "!=", "<", ">", "<=", ">=", "&&", "||", "and", "or", "not", "AND", "OR", "NOT"}:
            start_pos = pos
            if next_char in "=&|":  # ==, !=, <=, >=, &&, ||
                text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+2c"))
                pos = text_area.index(f"{pos}+2c")
            else:
                text_area.tag_add("logical_tag", pos, text_area.index(f"{pos}+1c"))
                pos = text_area.index(f"{pos}+1c")
            continue
        
        # Verificar operadores de asignación
        if (char == "=" and next_char != "=" ):
            text_area.tag_add("assign_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue
        elif char in "+-*/%^" and next_char == "=":
            text_area.tag_add("assign_tag", pos, text_area.index(f"{pos}+2c"))
            pos = text_area.index(f"{pos}+2c")
            continue
            
        # Verificar símbolos
        if char in {"(", ")", "{", "}", "[", "]", ";", ","}:
            text_area.tag_add("symbol_tag", pos, text_area.index(f"{pos}+1c"))
            pos = text_area.index(f"{pos}+1c")
            continue
            
        # Avanzar si no se aplica ninguna regla
        pos = text_area.index(f"{pos}+1c")