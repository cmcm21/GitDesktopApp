from PySide6.QtWidgets import QMainWindow, QPushButton, QMessageBox,QFrame
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Signal, QSize
from View.WindowID import WindowID
from View.UILoadingWidget import LoadingWidget
from View.EnterButton import EnterButton
from Utils.FileManager import FileManager


class BaseWindow(QMainWindow):
    window_closed = Signal()
    application_destroyed = Signal()

    def __init__(self, title: str, window_id: WindowID, width=500,  height=800):
        super().__init__()
        self.width = width
        self.height = height
        self.window_id = window_id

        self.loading: LoadingWidget = LoadingWidget(self)
        self.loading.hide()

        self.setWindowTitle(title)
        self.setBaseSize(QSize(width, height))
        self._set_window_icon()
        self.automatic_close = False

    def closeEvent(self, event):
        if self.automatic_close:
            event.accept()
        else:
            reply = QMessageBox.question(
                self,
                'Quit',
                'Are you sure you want to quit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
                self.application_destroyed.emit()
            else:
                event.ignore()

    def open(self):
        self.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout().update()

    @staticmethod
    def get_pixmap(img_name: str):
        pix_map = QPixmap(FileManager.get_img_path(img_name))
        return pix_map

    def _set_window_icon(self):
        self.setWindowIcon(QIcon(self.get_pixmap("soleil_default.jpg")))

    @staticmethod
    def create_default_frame(frame_name: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame.setLineWidth(2)
        frame.setObjectName(frame_name)
        return frame

    @staticmethod
    def create_button(parent, image_name: str = "", button_text: str = "") -> QPushButton:
        return EnterButton(
            icon=QIcon(BaseWindow.get_pixmap(image_name)),
            text=button_text,
            parent=parent
        )

    @staticmethod
    def throw_message_box(title: str, text: str, icon = QMessageBox.Icon.Information) -> bool:
        message_box = QMessageBox()
        message_box.setWindowTitle(title)
        message_box.setIcon(icon)
        message_box.setText(text)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        message_box.setDefaultButton(QMessageBox.StandardButton.Ok)

        reply = message_box.exec()

        return reply == QMessageBox.StandardButton.Ok