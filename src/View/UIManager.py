from .BaseWindow import BaseWindow
from .LauncherWindow import LauncherWindow
from enum import Enum


class WindowID(Enum):
    LOGGING = 0
    LAUNCHER = 1


class UIManager:
    """UIManager class is in charge of connect all the signal of the View part with the logical part"""
    def __init__(self):
        self.main_window = LauncherWindow()
        self.active_window: BaseWindow = None
        self.windows = {
            WindowID.LAUNCHER: self.main_window
        }

    def open_window(self, window_id: WindowID):
        if window_id not in self.windows:
            return

        if self.active_window is not None:
            self.active_window.close()

        self.active_window = self.windows[window_id]
        self.active_window.open()
