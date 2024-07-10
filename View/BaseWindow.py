from PySide6.QtWidgets import QMainWindow, QPushButton, QMessageBox, QWidget, QFrame
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Signal
from View.WindowID import WindowID
import os


class BaseWindow(QMainWindow):
    window_closed = Signal()

    def __init__(self, title: str, window_id: WindowID, width=500,  height=800):
        super().__init__()
        self.width = width
        self.height = height
        self.window_id = window_id

        self.setWindowTitle(title)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self._set_window_icon()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Quit',
            'Are you sure you want to quit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
            self.window_closed.emit()
        else:
            event.ignore()

    @staticmethod
    def get_pixmap(img_name: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../Resources/Img/", img_name)
        pix_map = QPixmap(icon_path)
        return pix_map

    def _set_window_icon(self):
        self.setWindowIcon(QIcon(self.get_pixmap("soleil_default.jpg")))

    @staticmethod
    def create_default_frame(frame_name: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setLineWidth(2)
        frame.setObjectName(frame_name)
        return frame

    @staticmethod
    def create_button(parent, image_name: str, button_text: str = "") -> QPushButton:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../Resources/Img/", image_name)
        pix_map = QPixmap(icon_path)
        return QPushButton(
            icon=QIcon(pix_map),
            text=button_text,
            parent=parent
        )

    def open(self):
        self.show()

    def close(self):
        self.hide()
