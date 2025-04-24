import tkinter as tk
from tkinter import filedialog


class FileManager:
    def __init__(self):
        self.current_file = None
        self.editor = None

    def set_editor(self, editor):
        self.editor = editor

    def new_file(self):
        if self.editor.get_text().strip():
            if self.ask_save_changes():
                self.save_file()
        self.editor.set_text("")  # Limpiar el editor
        self.current_file = None
        self.editor.update_line_numbers()  # Actualizar los números de línea

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.set_text(content)
                self.current_file = file_path
                self.editor.update_line_numbers()  # Actualizar los números de línea
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
                self.editor.set_text(content)
                self.current_file = file_path
                self.editor.update_line_numbers()  # Actualizar los números de línea

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
        else:
            self._save_to_file(self.current_file)
        self.editor.update_line_numbers()  # Actualizar los números de línea

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"),
                       ("Todos los archivos", "*.*")]
        )
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
        self.editor.update_line_numbers()  # Actualizar los números de línea

    def _save_to_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.editor.get_text())

    def close_file(self):
        if self.editor.get_text().strip():
            if self.ask_save_changes():
                self.save_file()
        self.editor.set_text("")  # Limpiar el editor
        self.current_file = None
        self.editor.update_line_numbers()  # Actualizar los números de línea

    def ask_save_changes(self):
        # Implementar diálogo para guardar cambios
        return False  # Simplificado por ahora
