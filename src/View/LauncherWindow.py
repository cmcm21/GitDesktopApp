from .BaseWindow import BaseWindow
from .UILogger import LoggerWidget
from .UIWorkspace import WorkspaceWidget
from .WindowID import WindowID
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QWidget,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
import os


class LauncherWindow(BaseWindow):
    def __init__(self, config: dict, window_id: WindowID, width=900, height=500):
        super(LauncherWindow, self).__init__("Rigging Launcher", window_id, width, height)
        self.config = config
        """Layouts"""
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()

        """Labels"""
        self.soleil_label = QLabel("Soleil")
        self.soleil_label.setObjectName("SoleilLabel")
        """Get Latest Button"""
        self.get_latest_btn = self._create_button("arrowDown.png", "Get latest")
        self.get_latest_btn.setObjectName("GetLatestButton")
        """Update Button"""
        self.update_btn = self._create_button("arrowUp.png", "Upload")
        self.update_btn.setObjectName("UpdateButton")
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
        self._build()

    def _create_button(self, image_name: str, button_text: str) -> QPushButton:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../../Resources/Img/", image_name)
        pix_map = QPixmap(icon_path)
        return QPushButton(
            icon=QIcon(pix_map),
            text=button_text,
            parent=self
        )

    def _build(self):
        """Header"""
        self.header_layout.addWidget(self.soleil_label)
        self.header_layout.addWidget(self.get_latest_btn, 0, Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addWidget(self.update_btn, 5, Qt.AlignmentFlag.AlignLeft)
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
        return

    def on_setup_completed(self, success: bool):
        if success:
            self.workspace.set_root_directory()

