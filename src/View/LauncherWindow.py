from .BaseWindow import BaseWindow
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QPushButton,
    QWidget,
)
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap
from PySide6.QtCore import QDir, QStandardPaths, QSize
import os


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class LauncherWindow(BaseWindow):
    def __init__(self, width=500, height=800):
        super(LauncherWindow, self).__init__("Rigging Launcher", width, height)
        """Layouts"""
        self.main_layout = QGridLayout()
        self.header_layout = QHBoxLayout()
        self.body_layout = QHBoxLayout()
        self.body_left = QVBoxLayout()
        self.body_right = QVBoxLayout()
        self.footer_layout = QHBoxLayout()

        """Buttons"""
        self.get_latest_btn = QPushButton("Get Latest")
        self.update_btn = QPushButton("Upload workspace")
        self.new_workspace_btn = QPushButton("New Workspace")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../../Resources/Img/", "mayaico.png")
        self.pixMap = QPixmap(icon_path)
        self.maya_btn = QPushButton(
            icon=QIcon(self.pixMap),
            text="Maya",
            parent=self
        )

        """Custom Widgets"""
        self.workspace = Color('red')
        self.dialog = Color('red')
        self._build()

    def _build(self):
        """Header"""
        self.header_layout.addWidget(self.get_latest_btn)
        self.header_layout.addWidget(self.update_btn)
        """Body left"""
        self.body_left.addWidget(self.new_workspace_btn)
        self.body_left.addWidget(self.maya_btn)
        """Body Right"""
        self.body_right.addWidget(self.workspace)
        self.body_right.addWidget(self.dialog)
        """Nesting Layouts"""
        self.body_layout.addLayout(self.body_left)
        self.body_layout.addLayout(self.body_right)

        self.main_layout.addLayout(self.header_layout, 0, 0)
        self.main_layout.addLayout(self.body_layout, 1, 0)
        self.main_layout.addLayout(self.footer_layout, 2, 0)
        """Set Main Layout"""
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        return
