import tkinter as tk


def es_palabra_valida(text_area, start_idx, end_idx, token_type):
    antes = text_area.get(f"{start_idx} -1c")
    despues = text_area.get(end_idx)

    # Los números siempre son válidos (no dependen de separadores)
    if token_type == "numero":
        return True

    # Los comentarios siempre son válidos (no dependen de separadores)
    elif token_type == "comentario":
        return True

    # Los operadores aritméticos y relacionales siempre deben ser válidos
    elif token_type in ["aritmetico", "relacional", "logico", "simbolo", "asignacion"]:
        return True

    # Para otros tokens, verificamos los separadores
    separadores = " \n\t.:,()[]{}+-*/=<>!\"'"
    return (antes in separadores or start_idx == "1.0") and (despues in separadores or despues == '')


def check_nums(text_area, pos_ini):
    # Configurar tag (hazlo una vez al inicio del programa)
    text_area.tag_config("number_tag", foreground="#0022FF")
    
    pos = pos_ini
    start = None
    tiene_punto = False
    while True:
        char = text_area.get(pos)  # Obtener carácter actual
        if char == "":  # Fin del texto
            if start is not None:
                text_area.tag_add("number_tag", start, pos)
            break
        
        # Lógica de validación
        if char in '+-' and pos == pos_ini:  # Signo al inicio
            start = pos
            pos = f"{pos}+1c"
        elif char.isdigit():
            if start is None:
                start = pos
            pos = f"{pos}+1c"
        elif char == '.' and not tiene_punto:
            tiene_punto = True
            if start is None:
                start = pos
            pos = f"{pos}+1c"
        else:  # Carácter no válido
            if start is not None:
                text_area.tag_add("number_tag", start, pos)  # Pintar número
                es_palabra_valida(text_area, start, pos, "numero")
            break



def resaltar_palabras(text_area):
    # Limpiar todos los tags
    for tag in text_area.tag_names():
        text_area.tag_remove(tag, "1.0", "end")

    # Crear tags para cada color y asociarlos con las palabras correspondientes
    color_palabras = {
        "#0022FF": {"0", "1", "2", "3", "4",
                    "5", "6", "7", "8", "9"},  # Números enteros
        "#800080": {"if", "then", "else", "end", "do", "while", "switch", "case", "int", "float", "main", "cin", "cout"},  # Palabras reservadas
        "#1D472B": {"//", "/*", "*/"},  # Comentarios
        "#958E12": {"+", "-", "*", "/", "%", "^", "++", "--"},  # Operadores aritméticos
        "#763A58": {"==", "!=", "<", ">", "<=", ">=", "&&", "||", "and", "or", "not", "AND", "OR", "NOT"},  # Operadores lógicos y relacionales
        "#FF00FF": {"(", ")", "{", "}", "[", "]", ";", ","},  # Símbolos
        "#1FBB9A": {"=", "+=", "-=", "*=", "/=", "%=", "^="}  # Asignación
    }

    # Configuración de los colores
    for color, palabras in color_palabras.items():
        text_area.tag_configure(color, foreground=color)

        for palabra in palabras:
            start = "1.0"
            while True:
                start = text_area.search(palabra, start,
                                         stopindex="end", nocase=False)
                if not start:
                    break
                end = f"{start}+{len(palabra)}c"

                # Ahora verificamos correctamente para cada tipo de token
                # if palabra in color_palabras["#0022FF"]:  # Números
                #     # Verificamos si es un número entero con o sin signo
                #     if es_palabra_valida(text_area, start, end, "numero"):
                #         text_area.tag_add(color, start, end)
                if any(caracter in "0123456789" for caracter in palabra):
                    # Obtiene la posición del primer carácter numérico
                    end = f"{start}+{len(palabra)}c"
                    check_nums(text_area, start)

                elif palabra in color_palabras["#800080"]:  # Palabras reservadas
                    if es_palabra_valida(text_area, start, end, "palabra_reservada"):
                        text_area.tag_add(color, start, end)
                
                elif palabra in color_palabras["#958E12"]:  # Operadores aritméticos
                    if es_palabra_valida(text_area, start, end, "aritmetico"):
                        text_area.tag_add(color, start, end)

                elif palabra in color_palabras["#1FBB9A"]:  # Asignacion
                    if es_palabra_valida(text_area, start, end, "asignacion"):
                        text_area.tag_add(color, start, end)

                elif palabra in color_palabras["#763A58"]:  # Operadores lógicos
                    if es_palabra_valida(text_area, start, end, "logico"):
                        text_area.tag_add(color, start, end)

                elif palabra in color_palabras["#FF00FF"]:  # Símbolos
                    if es_palabra_valida(text_area, start, end, "simbolo"):
                        text_area.tag_add(color, start, end)

                elif palabra in color_palabras["#1D472B"]:  # Comentarios
                    if palabra == "//":  # Comentarios de una línea
                        end_line = text_area.search("\n", end, stopindex="end")
                        if not end_line:
                            end_line = "end"
                        text_area.tag_add(color, start, end_line)
                    elif palabra == "/*":  # Comentarios multilínea
                        end_comment = text_area.search("*/", end, stopindex="end")
                        if end_comment:
                            text_area.tag_add(color, start, end_comment + "+2c")  # +2 para incluir el */
                        else:
                            text_area.tag_add(color, start, "end")  # Si no cierra, se resalta hasta el final

                start = end  # Continuar buscando la siguiente instancia