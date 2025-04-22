import tkinter as tk
from tkinter import ttk


class CodeEditor:
    def __init__(self, parent):
        self.parent = parent
        self.text_area = None
        self.line_numbers = None
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

        # Números de línea
        self.line_numbers = tk.Text(
            self.editor_frame,
            width=4,
            padx=5,
            bg="lightgray",
            bd=0,
            state="disabled"
        )

        # Scrollbars
        self.scroll_y = tk.Scrollbar(self.editor_frame, orient="vertical")
        self.scroll_x = tk.Scrollbar(self.editor_frame, orient="horizontal")

        # Empaquetado
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.editor_frame.pack(fill=tk.BOTH, expand=True)

    def setup_bindings(self):
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<ButtonRelease-1>", self.update_line_numbers)

    def update_line_numbers(self, event=None):
        # Implementación simplificada
        line_count = self.text_area.index("end-1c").split(".")[0]
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in
                                                  range(1, int(line_count)+1)))
        self.line_numbers.config(state="disabled")

    def get_text(self):
        return self.text_area.get("1.0", tk.END)

    def set_text(self, text):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
