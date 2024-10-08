from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QDialog,
    QLabel
)
from PySide6.QtCore import QTimer, Qt, QSize, Signal
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import QGraphicsOpacityEffect
from Utils.FileManager import FileManager


class LoadingWindows(QDialog):
    close_event = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.custom_parent = parent

        # Create a QLabel widget
        self.label = QLabel(self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set window opacity (0.0 = fully transparent, 1.0 = fully opaque)
        self.setWindowOpacity(0.5)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.setGraphicsEffect(opacity_effect)

        # Create QMovie object and load the GIF
        gif_path = FileManager.get_img_path("loading_2.gif")
        self.movie = QMovie(gif_path)

        # Set the QMovie object on the QLabel
        self.label.setMovie(self.movie)
        self.label.resize(QSize(128,128))
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: black;")

        # Start the animation
        self.movie.start()

        # Create layout and add the label
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignJustify)
        self.setLayout(layout)
        self.maximumSize()

    def start(self):
        self.movie.start()

    def stop(self):
        self.movie.stop()
        self.close_event.emit()
        self.close()