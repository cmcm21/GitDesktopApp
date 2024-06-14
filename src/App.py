from PySide6.QtWidgets import QApplication
from View.UIManager import UIManager
from View.UIManager import WindowID
import os


class Application:
    def __init__(self):
        self.app = QApplication([])

        script_dir = os.path.dirname(os.path.abspath(__file__))
        dark_theme_path = os.path.join(script_dir, "./View/", "dark_theme.qss")
        with open(dark_theme_path, "r") as file:
            qss = file.read()
            self.app.setStyleSheet(qss)

        self.ui_manager = UIManager()

    def run(self):
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self.app.exec()

