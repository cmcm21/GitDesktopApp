from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.UILogger import LoggerWidget
from View.UIWorkspace import WorkspaceWidget
from View.UICommitWindow import CommitWindow
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QWidget,
)
from PySide6.QtCore import Qt, Signal, Slot


class LauncherWindow(BaseWindow):
    upload_repository_signal = Signal(str)
    window_closed = Signal()

    def __init__(self, config: dict, window_id: WindowID, width=900, height=500):
        super(LauncherWindow, self).__init__("Rigging Launcher", window_id, width, height)
        self.config = config
        self.commit_window = None
        self._create_all_element()
        self._build()
        self._connect_buttons()

    def _create_all_element(self):
        """Layouts"""
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()
        """Get Latest Button"""
        self.get_latest_btn = self._create_button("arrowDown.png", "Get latest")
        self.get_latest_btn.setObjectName("GetLatestButton")
        """Update Button"""
        self.upload_btn = self._create_button("arrowUp.png", "Upload")
        self.upload_btn.setObjectName("UpdateButton")
        """New Workspace Button"""
        self.new_workspace_btn = self._create_button("plus.png", "")
        self.new_workspace_btn.setToolTip("New Workspace")
        self.new_workspace_btn.setObjectName("NewWorkspaceButton")
        """Open Maya Button"""
        self.maya_btn = self._create_button("mayaico.png", "")
        self.maya_btn.setToolTip("Open Maya")
        self.maya_btn.setObjectName("MayaButton")
        """Connect Button"""
        self.connect_button = self._create_button("singleplayer.png", "Connect")
        self.connect_button.setObjectName("ConnectButton")
        """Custom Widgets"""
        self.workspace = WorkspaceWidget(self.config["general"]["working_path"])
        self.logger_widget = LoggerWidget()

    def _build(self):
        """Header"""
        self.header_layout.addWidget(self.get_latest_btn, 5, Qt.AlignmentFlag.AlignRight)
        self.header_layout.addWidget(self.upload_btn, 0, Qt.AlignmentFlag.AlignRight)
        """Body left"""
        self.body_left.addWidget(self.new_workspace_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.body_left.addWidget(self.maya_btn, 5, Qt.AlignmentFlag.AlignTop)
        """Body Right"""
        self.body_right.addWidget(self.workspace)
        self.body_right.addWidget(self.logger_widget)
        """Nesting Layouts"""
        self.body_layout.addLayout(self.body_left, 1)
        self.body_layout.addLayout(self.body_right, 6)
        """Main Layout"""
        self.main_layout.addLayout(self.header_layout, 0, 0)
        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.footer_layout, 2, 0)
        self.main_layout.setSpacing(20)
        """Set Main Layout"""
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def _connect_buttons(self):
        self.upload_btn.clicked.connect(self, self.create_commit_windows)
        return

    def create_commit_windows(self):
        self.commit_window = CommitWindow()
        self.commit_window.show()
        self.commit_window.accept_clicked_signal.connect(self._on_commit_window_accept)
        self.commit_window.cancel_clicked_signal.connect(self._on_commit_window_cancel)

    @Slot(str)
    def _on_commit_window_accept(self, message):
        self.upload_repository_signal.emit(message)
        self._close_commit_window()

    @Slot()
    def _on_commit_window_cancel(self):
        self._close_commit_window()

    def _close_commit_window(self):
        if self.commit_window is not None:
            self.commit_window.close()
            self.commit_window = None
        return

    def on_setup_completed(self, success: bool):
        self.workspace.set_root_directory()
