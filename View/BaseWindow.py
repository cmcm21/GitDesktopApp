from PySide6.QtWidgets import QMainWindow, QPushButton, QMessageBox, QWidget, QFrame
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Signal
from View.WindowID import WindowID
from View.UILoadingWidget import LoadingWidget
from Utils.FileManager import FileManager
import os


class BaseWindow(QMainWindow):
    window_closed = Signal()

    def __init__(self, title: str, window_id: WindowID, width=500,  height=800):
        super().__init__()
        self.width = width
        self.height = height
        self.window_id = window_id
        self.loading: LoadingWidget = LoadingWidget(self)
        self.loading.hide()

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
        img_path = FileManager.get_img_path()
        icon_path = os.path.join(img_path, img_name)
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
        return QPushButton(
            icon=QIcon(BaseWindow.get_pixmap(image_name)),
            text=button_text,
            parent=parent
        )

    def open(self):
        self.show()

    def close(self):
        self.hide()
