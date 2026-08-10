from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtWidgets import QMenuBar

class MenuBar(QMenuBar):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.file_menu = self.addMenu("File")
        self.language_menu = self.addMenu("language")

        self.new_action = self.file_menu.addAction("New")
        self.open_action = self.file_menu.addAction("Open")
        self.save_action = self.file_menu.addAction("Save")

        self.save_action.setShortcut("Ctrl+S")

        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("Exit")

        self.cpp_action = self.language_menu.addAction("C++")
        self.python_action = self.language_menu.addAction("PYTHON")