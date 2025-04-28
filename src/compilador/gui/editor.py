import tkinter as tk
from analizadores.lexico import resaltar_palabras

class CodeEditor:
    def __init__(self, parent):
        self.parent = parent
        self.text_area = None
        self.line_numbers = None
        self.line_label = None
        self.col_label = None
        self.status_bar = None
        self.create_widgets()
        self.setup_bindings()

    def create_widgets(self):
        # Frame principal
        self.editor_frame = tk.Frame(self.parent)

        # Área de texto
        self.text_area = tk.Text(
            self.editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Courier", 10)
        )

        # Scrollbars
        self.scroll_y = tk.Scrollbar(self.editor_frame, orient="vertical")

        # Números de línea
        self.line_numbers = tk.Text(
            self.editor_frame,
            width=4,
            padx=5,
            bg="lightgray",
            bd=0,
            height=30,
            font=("Courier", 10),
            state="disabled",
            yscrollcommand=self.scroll_y.set
        )

        # Empaquetado
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, pady=(23, 0))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(23, 0))

        self.scroll_y.config(
            command=lambda *args: [self.line_numbers.yview(*args),
                                   self.text_area.yview(*args)])
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y, pady=(23, 0))

        self.scroll_x = tk.Scrollbar(self.editor_frame, orient="horizontal",
                                     command=self.text_area.xview)

        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(wrap="none", xscrollcommand=self.scroll_x.set)

        # Agregando Labels para mostrar Linea: Columna
        # Crear un frame contenedor para la barra de estado
        self.status_bar = tk.Frame(self.parent, height=20, bg="#e0e0e0")
        self.status_bar.pack(side=tk.TOP, fill=tk.X)

        # Crear el label de línea
        self.line_label = tk.Label(self.status_bar,
                                   text="Línea: 1", anchor="w", bg="#e0e0e0")
        self.line_label.pack(side=tk.LEFT, padx=10)

        # Crear el label de columna
        self.col_label = tk.Label(self.status_bar,
                                  text="Columna: 1", anchor="w", bg="#e0e0e0")
        self.col_label.pack(side=tk.LEFT, padx=10)

    def update_after_realize(self, event=None):
        # Actualiza el área de texto después de realizar cambios
        self.update_line_numbers(None)
        resaltar_palabras(self.text_area)

    def setup_bindings(self):
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        #evento cuando escribe algo una letra, pero no teclas especiales como Ctrl, Shift, etc.
        self.text_area.bind("<KeyPress>", self.update_after_realize)
        self.text_area.bind("<ButtonRelease-1>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)
        self.text_area.bind("<Configure>", self.update_line_numbers)
        self.text_area.bind("<Up>", self.update_line_numbers)
        self.text_area.bind("<Down>", self.update_line_numbers)
        self.text_area.bind("<Shift-MouseWheel>", self.sync_h_scroll)
        

    def update_line_numbers(self, event=None):
        # Implementación simplificada
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        line_count = self.text_area.index("end-1c").split(".")[0]
        line_numbers_string = "\n".join(str(i)
                                        for i in range(1, int(line_count) + 1))
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state="disabled")

        # sincronizar el desplazamiento vertical
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

        # Actualizar etiquetas de línea y columna
        self.update_line_column()
        # Llamar al analizador lexico

    # Función para sincronizar el desplazamiento horizontal
    def sync_h_scroll(self):
        self.text_area.xview_moveto(self.scroll_x.get()[0])

    def update_line_column(self):
        index = self.text_area.index(tk.INSERT)
        line = index.split(".")[0]
        column = int(index.split(".")[1]) + 1
        self.line_label.config(text=f"Línea: {line}")
        self.col_label.config(text=f"Columna: {column}")

    def get_text(self):
        return self.text_area.get("1.0", tk.END)

    def set_text(self, text):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
