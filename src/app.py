import tkinter as tk

# Crear ventana
root = tk.Tk()
root.title("Mi primera ventana")  # Título de la ventana
root.geometry("400x300")  # Tamaño de la ventana (ancho x alto)

# Etiqueta dentro de la ventana
label = tk.Label(root, text="¡Hola, mundo!", font=("Arial", 14))
label.pack(pady=20)

# Botón dentro de la ventana
button = tk.Button(root, text="Haz clic", command=lambda: print("Botón presionado"))
button.pack()

# Iniciar la aplicación
root.mainloop()
