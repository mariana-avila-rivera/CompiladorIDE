# App.py
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
        self.setup_ui()

    def setup_ui(self):
        # Configurar la interfaz
        self.file_manager = FileManager(self.root)
        self.menu = MenuBar(self.root, self.file_manager)
        
        # Crear la toolbar pasándole las referencias necesarias (ahora antes del editor)
        self.toolbar = Toolbar(self.root, self.file_manager)
        self.toolbar.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Panel principal para la división vertical (ahora hijo de root)
        self.main_panel = tk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True)

        # Editor de código (ahora directamente en main_panel)
        self.editor = CodeEditor(self.main_panel)
        self.main_panel.add(self.editor.editor_frame, stretch="always")

        # Paneles inferiores (ahora directamente en main_panel)
        self.panels = BottomPanels(self.main_panel)
        self.main_panel.add(self.panels.main_panel, stretch="always") # Asegúrate de usar panels.main_panel

        # Actualizar la referencia del editor y panels en la toolbar
        self.toolbar.editor = self.editor
        self.toolbar.bottom_panels = self.panels

        # Configurar eventos
        self.file_manager.set_editor(self.editor)

    def run(self):
        self.root.mainloop()