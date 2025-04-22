import tkinter as tk
from gui.menu import MenuBar
from gui.toolbar import Toolbar
from gui.editor import CodeEditor
from gui.panels import BottomPanels
from core.file_manager import FileManager


class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador")
        self.root.geometry("900x600")

        self.file_manager = FileManager()
        self.setup_ui()

    def setup_ui(self):
        # Configurar la interfaz
        self.menu = MenuBar(self.root, self.file_manager)
        self.toolbar = Toolbar(self.root, self.file_manager)
        self.editor = CodeEditor(self.root)
        self.panels = BottomPanels(self.root)

        # Configurar eventos
        self.file_manager.set_editor(self.editor)

    def run(self):
        self.root.mainloop()
