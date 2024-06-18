from PySide6.QtWidgets import QApplication
from View.UIManager import UIManager
from View.UIManager import WindowID
from Controller.GitController import GitController
import tomli
import os


class ConfigManager:
    def __init__(self):
        return

    @staticmethod
    def get_config() -> dict:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(script_dir, "../", "configFile.toml")
        with open(config_file_path, "rb") as config_file:
            config = tomli.load(config_file)

        return config


class Application:
    def __init__(self):
        self.app = QApplication([])
        self._set_style_sheet()
        self.config = ConfigManager.get_config()
        self.ui_manager = UIManager(self.config)
        self.logger = self.ui_manager.logger
        self.git_controller = GitController(self.config, self.logger)
        self.connect_git_controller_ui_manager()
        self.git_controller.setup()

    def connect_git_controller_ui_manager(self):
        self.git_controller.setup_completed.connect(self.ui_manager.on_setup_completed)
        self.ui_manager.lw_get_latest_clicked.connect(self.git_controller.get_latest)
        self.ui_manager.lw_uploaded_clicked.connect(self.git_controller.push_changes)

    def _set_style_sheet(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dark_theme_path = os.path.join(script_dir, "./View/", "appStyle.qss")
        with open(dark_theme_path, "r") as file:
            qss = file.read()
            self.app.setStyleSheet(qss)

    def run(self):
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self.app.exec()

