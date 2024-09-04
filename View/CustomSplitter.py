from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QSplitterHandle, QTextEdit, QVBoxLayout, QWidget
from PySide6.QtGui import QColor, QPainter, QBrush
from PySide6.QtCore import Qt

class CustomSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.is_hovered = False

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()  # Repaint the handle
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()  # Repaint the handle
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.is_hovered:
            # Highlight the handle (for example, with a blue color)
            color = QColor("#1E90FF")
        else:
            # Default color
            color = QColor("#111111")

        if self.orientation() == Qt.Orientation.Vertical:
            self.setFixedHeight(3)
        else:
            self.setFixedWidth(3)

        painter.fillRect(self.rect(), QBrush(color))

class CustomSplitter(QSplitter):
    handle = None

    def createHandle(self):
        self.handle = CustomSplitterHandle(self.orientation(), self)
        return self.handle