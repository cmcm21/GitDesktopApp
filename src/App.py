from PySide6.QtWidgets import QApplication
from View.UIManager import UIManager
from View.UIManager import WindowID
from Controller.GitController import GitController
from Controller.SystemController import SystemController
from PySide6.QtCore import QThread, Signal, Slot
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


class Application(QApplication):

    git_setup = Signal()
    system_controller_setup = Signal()

    def __init__(self):
        super().__init__([])
        self._set_style_sheet()
        self.config = ConfigManager.get_config()
        self.ui_manager = UIManager(self.config)
        self.logger = self.ui_manager.logger
        self.git_installed = False
        self._create_git_controller_thread()
        self._create_system_controller_thread()

    def _create_git_controller_thread(self):
        self.git_controller_thread = QThread(self)
        self.git_controller = GitController(self.config)

        self.git_controller.setup_completed.connect(self.ui_manager.on_setup_completed)
        self.git_controller.log_message.connect(self.ui_manager.on_log_signal_received)
        self.git_controller.error_message.connect(self.ui_manager.on_err_signal_received)
        self.git_setup.connect(self.git_controller.setup)

        self.ui_manager.lw_get_latest_clicked.connect(self.git_controller.get_latest)
        self.ui_manager.lw_uploaded_clicked.connect(self.git_controller.push_changes)
        self.git_controller.moveToThread(self.git_controller_thread)
        self.git_controller_thread.start()

    def _create_system_controller_thread(self):
        self.system_controller_thread = QThread(self)
        self.system_controller = SystemController(self.config)

        self.system_controller.log_message.connect(self.ui_manager.on_log_signal_received)
        self.system_controller.error_message.connect(self.ui_manager.on_err_signal_received)

        self.system_controller.maya_checked.connect(self.ui_manager.on_maya_checked)
        self.system_controller.git_checked.connect(self.on_git_checked)
        self.system_controller.git_installed.connect(self.on_git_installed)
        self.system_controller.setup_finished.connect(self.on_system_controller_setup_finished)
        self.system_controller_setup.connect(self.system_controller.setup)

        self.ui_manager.lw_open_maya_clicked.connect(self.system_controller.open_maya)
        self.system_controller.moveToThread(self.system_controller_thread)
        self.system_controller_thread.start()

    @Slot()
    def on_system_controller_setup_finished(self):
        if self.git_installed:
            self.git_setup.emit()

    @Slot(bool)
    def on_git_checked(self, success: bool):
        print("Git is Installed: " + str(success))
        self.git_installed = success

    @Slot(bool)
    def on_git_installed(self, success: bool):
        if self.git_installed:
            return

        self.git_installed = success
        if self.git_installed:
            self.git_setup.emit()

    def _set_style_sheet(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dark_theme_path = os.path.join(script_dir, "./View/", "appStyle.qss")
        with open(dark_theme_path, "r") as file:
            qss = file.read()
            self.setStyleSheet(qss)

    def run(self):
        self.ui_manager.open_window(WindowID.LAUNCHER)
        self.system_controller_setup.emit()
        self.exec()

