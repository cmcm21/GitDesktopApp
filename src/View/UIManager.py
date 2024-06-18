from .LauncherWindow import LauncherWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot, Signal, QObject
from .WindowID import WindowID


class UIManager(QObject):
    """Launcher window buttons signals"""
    lw_get_latest_clicked = Signal()
    lw_uploaded_clicked = Signal(str)
    lw_open_maya_clicked = Signal()
    lw_new_workspace_clicked = Signal()

    def __init__(self, config: dict):
        super().__init__()
        self.launcher_window = LauncherWindow(config, WindowID.LAUNCHER)
        self.logger = self.launcher_window.logger_widget.logger
        self.connect_button: QPushButton = self.launcher_window.connect_button
        self.windows = {
            WindowID.LAUNCHER: self.launcher_window
        }
        self.config = config
        self._connect_launcher_windows()

    def open_window(self, window_id: WindowID):
        if window_id not in self.windows:
            return

        if self.launcher_window is not None:
            self.launcher_window.close()

        self.launcher_window = self.windows[window_id]
        self.launcher_window.open()

    def _connect_launcher_windows(self):
        self.launcher_window.get_latest_btn.clicked.connect(lambda: self.lw_get_latest_clicked.emit())
        self.launcher_window.upload_repository_signal.connect(lambda message: self.lw_uploaded_clicked.emit(message))

    @Slot(bool)
    def on_setup_completed(self, success: bool):
        if self.launcher_window.window_id != WindowID.LAUNCHER:
            return
        self.launcher_window.on_setup_completed(success)
