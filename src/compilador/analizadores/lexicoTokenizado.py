import tkinter as tk


def pintado (palabra, tipo):
    color_palabras = {
       "numero":"red"
    }

    # Configuración de los colores
    for color, palabras in color_palabras.items():
        text_area.tag_configure(color, foreground=color)

 def tokenizado(text_area):
        texto = text_area.get("1.0", tk.END)
        estado = 0
        pos = "1.0"
        in_comment = False

        while pos != tk.END:
            char = texto.get(pos)
            if estado == 0:
                if char in "0123456789":
                    
                if char in "0123456789":
                    pos = f"{pos}+1c"
                else:
                    estado = 0
                    # Aquí puedes agregar el token a una lista o hacer algo con él
                    print(f"Token encontrado: {texto.get(pos)}")