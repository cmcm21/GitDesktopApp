from .LauncherWindow import LauncherWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot
from .WindowID import WindowID


class UIManager:
    """UIManager class is in charge of connect all the signal of the View part with the logical part"""
    def __init__(self, config: dict):
        self.launcher_window = LauncherWindow(config, WindowID.LAUNCHER)
        self.logger = self.launcher_window.logger_widget.logger
        self.connect_button: QPushButton = self.launcher_window.connect_button
        self.windows = {
            WindowID.LAUNCHER: self.launcher_window
        }
        self.config = config

    def open_window(self, window_id: WindowID):
        if window_id not in self.windows:
            return

        if self.launcher_window is not None:
            self.launcher_window.close()

        self.launcher_window = self.windows[window_id]
        self.launcher_window.open()

    @Slot(bool)
    def on_setup_completed(self, success: bool):
        if self.launcher_window.window_id != WindowID.LAUNCHER:
            return
        self.launcher_window.on_setup_completed(success)
